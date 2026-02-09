"""Admin routes for dashboard and management."""
from flask import Blueprint, request, jsonify
from datetime import datetime, date, timedelta
from marshmallow import ValidationError
from app import db
from app.models import Order, User, Restaurant, Menu
from app.schemas import OrderStatusUpdateSchema
from app.services.order_service import OrderService
from app.services.reminder_service import ReminderService
from app.tasks.order_tasks import generate_restaurant_summary_for_date
from app.middleware.auth import admin_required
from app.utils.decorators import validate_json, paginated
from app.utils.helpers import paginate_query

bp = Blueprint('admin', __name__, url_prefix='/api/admin')

order_status_update_schema = OrderStatusUpdateSchema()


@bp.route('/dashboard', methods=['GET'])
@admin_required
def get_dashboard_stats(user):
    """Get admin dashboard statistics."""
    today = date.today()
    week_from = today
    week_to = today + timedelta(days=7)
    
    # Total stats
    total_users = User.query.filter_by(is_active=True).count()
    total_restaurants = Restaurant.query.filter_by(is_active=True).count()
    total_menus = Menu.query.filter_by(is_active=True).count()
    
    # Orders this week
    orders_this_week = Order.query.filter(
        Order.order_date >= week_from,
        Order.order_date <= week_to
    ).count()
    
    # Orders today
    orders_today = Order.query.filter_by(order_date=today).count()
    
    # Users without orders for tomorrow
    tomorrow = today + timedelta(days=1)
    users_without_orders = ReminderService.get_users_without_orders(tomorrow)
    
    # Recent orders
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(10).all()
    
    # Orders by status
    orders_by_status = db.session.query(
        Order.status,
        db.func.count(Order.id)
    ).filter(
        Order.order_date >= week_from,
        Order.order_date <= week_to
    ).group_by(Order.status).all()
    
    status_counts = {status: count for status, count in orders_by_status}
    
    return jsonify({
        'stats': {
            'total_users': total_users,
            'total_restaurants': total_restaurants,
            'total_menus': total_menus,
            'orders_this_week': orders_this_week,
            'orders_today': orders_today,
            'users_without_orders_tomorrow': len(users_without_orders)
        },
        'status_breakdown': status_counts,
        'recent_orders': [order.to_dict() for order in recent_orders]
    }), 200


@bp.route('/orders', methods=['GET'])
@admin_required
@paginated(default_per_page=50, max_per_page=200)
def get_all_orders(user, page, per_page):
    """Get all orders with filters."""
    query = Order.query
    
    # Filter by date
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    
    if date_from:
        query = query.filter(Order.order_date >= datetime.strptime(date_from, '%Y-%m-%d').date())
    if date_to:
        query = query.filter(Order.order_date <= datetime.strptime(date_to, '%Y-%m-%d').date())
    
    # Filter by status
    status = request.args.get('status')
    if status:
        query = query.filter_by(status=status)
    
    # Filter by restaurant
    restaurant_id = request.args.get('restaurant_id')
    if restaurant_id:
        query = query.filter_by(restaurant_id=int(restaurant_id))
    
    # Order by date
    query = query.order_by(Order.order_date.desc(), Order.created_at.desc())
    
    # Paginate
    result = paginate_query(query, page=page, per_page=per_page)
    
    return jsonify({
        'orders': [order.to_dict(include_items=True) for order in result['items']],
        'pagination': {
            'total': result['total'],
            'page': result['page'],
            'per_page': result['per_page'],
            'pages': result['pages']
        }
    }), 200


@bp.route('/orders/summary', methods=['GET'])
@admin_required
def get_orders_summary(user):
    """Get order summary for a date range."""
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    
    if not date_from or not date_to:
        return jsonify({'error': 'date_from and date_to are required'}), 400
    
    date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
    date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
    
    # Get orders in date range
    orders = Order.query.filter(
        Order.order_date >= date_from_obj,
        Order.order_date <= date_to_obj
    ).all()
    
    # Group by date and restaurant
    summary_by_date = {}
    
    for order in orders:
        date_key = order.order_date.isoformat()
        if date_key not in summary_by_date:
            summary_by_date[date_key] = {
                'date': date_key,
                'total_orders': 0,
                'total_amount': 0,
                'by_restaurant': {}
            }
        
        summary_by_date[date_key]['total_orders'] += 1
        summary_by_date[date_key]['total_amount'] += float(order.total_amount)
        
        rest_id = order.restaurant_id
        if rest_id not in summary_by_date[date_key]['by_restaurant']:
            summary_by_date[date_key]['by_restaurant'][rest_id] = {
                'restaurant_id': rest_id,
                'restaurant_name': order.restaurant.name,
                'order_count': 0,
                'total_amount': 0
            }
        
        summary_by_date[date_key]['by_restaurant'][rest_id]['order_count'] += 1
        summary_by_date[date_key]['by_restaurant'][rest_id]['total_amount'] += float(order.total_amount)
    
    # Convert to list
    summary_list = []
    for date_summary in summary_by_date.values():
        date_summary['by_restaurant'] = list(date_summary['by_restaurant'].values())
        summary_list.append(date_summary)
    
    # Sort by date
    summary_list.sort(key=lambda x: x['date'])
    
    return jsonify({
        'summary': summary_list,
        'date_from': date_from,
        'date_to': date_to
    }), 200


@bp.route('/orders/<int:order_id>/status', methods=['PUT'])
@admin_required
@validate_json
def update_order_status(user, order_id):
    """Update order status."""
    try:
        data = order_status_update_schema.load(request.json)
        
        order = OrderService.update_order_status(order_id, data['status'])
        
        return jsonify({
            'message': 'Order status updated',
            'order': order.to_dict()
        }), 200
        
    except ValidationError as e:
        return jsonify({'error': 'Validation error', 'messages': e.messages}), 400
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@bp.route('/orders/send-to-restaurant', methods=['POST'])
@admin_required
@validate_json
def send_orders_to_restaurant(user):
    """Manually send orders to restaurant for a specific date."""
    try:
        restaurant_id = request.json.get('restaurant_id')
        target_date = request.json.get('date')
        
        if not restaurant_id or not target_date:
            return jsonify({'error': 'restaurant_id and date are required'}), 400
        
        target_date_obj = datetime.strptime(target_date, '%Y-%m-%d').date()
        
        success, message = generate_restaurant_summary_for_date(restaurant_id, target_date_obj)
        
        if success:
            return jsonify({'message': message}), 200
        else:
            return jsonify({'error': message}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/users-without-orders', methods=['GET'])
@admin_required
def get_users_without_orders(user):
    """Get users who haven't ordered for a specific date."""
    target_date = request.args.get('date')
    
    if not target_date:
        # Default to tomorrow
        target_date = (date.today() + timedelta(days=1)).isoformat()
    
    target_date_obj = datetime.strptime(target_date, '%Y-%m-%d').date()
    
    users = ReminderService.get_users_without_orders(target_date_obj)
    
    return jsonify({
        'date': target_date,
        'count': len(users),
        'users': [u.to_dict() for u in users]
    }), 200


@bp.route('/reports/orders', methods=['GET'])
@admin_required
def get_order_report(user):
    """Generate order report."""
    # Get date range (default to last 30 days)
    date_to = date.today()
    date_from = date_to - timedelta(days=30)
    
    if request.args.get('date_from'):
        date_from = datetime.strptime(request.args.get('date_from'), '%Y-%m-%d').date()
    if request.args.get('date_to'):
        date_to = datetime.strptime(request.args.get('date_to'), '%Y-%m-%d').date()
    
    # Get orders
    orders = Order.query.filter(
        Order.order_date >= date_from,
        Order.order_date <= date_to
    ).all()
    
    # Calculate stats
    total_orders = len(orders)
    total_revenue = sum(float(order.total_amount) for order in orders)
    avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
    
    # Orders by restaurant
    by_restaurant = {}
    for order in orders:
        rest_id = order.restaurant_id
        if rest_id not in by_restaurant:
            by_restaurant[rest_id] = {
                'restaurant_id': rest_id,
                'restaurant_name': order.restaurant.name,
                'order_count': 0,
                'total_revenue': 0
            }
        by_restaurant[rest_id]['order_count'] += 1
        by_restaurant[rest_id]['total_revenue'] += float(order.total_amount)
    
    return jsonify({
        'date_from': date_from.isoformat(),
        'date_to': date_to.isoformat(),
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'average_order_value': avg_order_value,
        'by_restaurant': list(by_restaurant.values())
    }), 200
