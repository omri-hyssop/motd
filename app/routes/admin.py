"""Admin routes for dashboard and management."""
from flask import Blueprint, request, jsonify, current_app
from datetime import datetime, date, timedelta
from marshmallow import ValidationError
from app import db
from app.models import Order, User, Restaurant, Menu, RestaurantOrderEmailLog, RestaurantAvailability, MotdOption
from app.schemas import OrderStatusUpdateSchema
from app.services.order_service import OrderService
from app.services.reminder_service import ReminderService
from app.tasks.order_tasks import generate_restaurant_summary_for_date
from app.middleware.auth import admin_required
from app.utils.decorators import validate_json, paginated
from app.utils.helpers import paginate_query
from app.models import RestaurantAvailability

bp = Blueprint('admin', __name__, url_prefix='/api/admin')

order_status_update_schema = OrderStatusUpdateSchema()

WEEKDAY_LABELS = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']

def _order_summary_line(order: Order) -> str:
    user_label = None
    try:
        user_label = order.user.full_name if order.user else None
    except Exception:
        user_label = None
    user_label = user_label or f"User {order.user_id}"

    text = (order.order_text or '').strip()
    if not text and getattr(order, 'items', None):
        # Structured order fallback
        parts = []
        for item in order.items:
            try:
                parts.append(f"{item.quantity}x {item.menu_item_name}")
            except Exception:
                continue
        text = ", ".join(parts).strip()
    if not text:
        text = "(no order details)"

    notes = (order.notes or '').strip()
    if notes:
        return f"- {user_label}: {text} (Notes: {notes})"
    return f"- {user_label}: {text}"


def _build_restaurant_email_draft(target_date_obj: date, restaurant: Restaurant, orders: list[Order]) -> dict:
    friendly_date = target_date_obj.strftime('%A, %b %d, %Y')
    subject = f"Meal of the Day orders for {friendly_date}"

    lines = [
        f"Hello {restaurant.contact_name or restaurant.name},",
        "",
        f"Here are the orders for {friendly_date}:",
        "",
    ]
    if not orders:
        lines.append("(No orders)")
    else:
        for o in orders:
            lines.append(_order_summary_line(o))
    lines.extend(["", "Thanks,", "Meal of the Day"])

    return {
        "to": restaurant.email,
        "restaurant_id": restaurant.id,
        "restaurant_name": restaurant.name,
        "subject": subject,
        "body": "\n".join(lines),
    }


@bp.route('/motd', methods=['GET'])
@admin_required
def list_motd_options(user):
    """List MOTD options for a weekday, scoped to restaurants available that day."""
    weekday_param = request.args.get('weekday')
    if weekday_param is None:
        weekday = date.today().weekday()
    else:
        try:
            weekday = int(weekday_param)
        except Exception:
            return jsonify({'error': 'weekday must be an integer 0-6'}), 400

    if weekday > 4:
        return jsonify({'weekday': weekday, 'restaurants': []}), 200

    available_ids = [
        r.restaurant_id
        for r in RestaurantAvailability.query.filter_by(weekday=weekday, is_available=True).all()
    ]
    if not available_ids:
        return jsonify({'weekday': weekday, 'restaurants': []}), 200

    restaurants = Restaurant.query.filter(Restaurant.id.in_(available_ids), Restaurant.is_active.is_(True)).order_by(Restaurant.name).all()
    motd_rows = MotdOption.query.filter(MotdOption.weekday == weekday, MotdOption.restaurant_id.in_(available_ids)).all()
    motd_by_rest = {m.restaurant_id: m for m in motd_rows}

    result = []
    for r in restaurants:
        m = motd_by_rest.get(r.id)
        result.append({
            'restaurant': {'id': r.id, 'name': r.name, 'email': r.email},
            'motd_option': m.option_text if m else None,
            'motd_option_id': m.id if m else None,
        })

    return jsonify({'weekday': weekday, 'restaurants': result}), 200


@bp.route('/motd', methods=['PUT'])
@admin_required
@validate_json
def upsert_motd_option(user):
    """Create/update (or clear) a MOTD option. Body: {weekday, restaurant_id, option_text}."""
    weekday_param = request.json.get('weekday')
    restaurant_id = request.json.get('restaurant_id')
    option_text = request.json.get('option_text')
    if not restaurant_id:
        return jsonify({'error': 'restaurant_id is required'}), 400
    if weekday_param is None:
        weekday = date.today().weekday()
    else:
        try:
            weekday = int(weekday_param)
        except Exception:
            return jsonify({'error': 'weekday must be an integer 0-6'}), 400
    if weekday < 0 or weekday > 6:
        return jsonify({'error': 'weekday must be in range 0-6'}), 400

    restaurant = db.session.get(Restaurant, int(restaurant_id))
    if not restaurant:
        return jsonify({'error': 'Restaurant not found'}), 404

    # Empty/blank clears
    if option_text is None or str(option_text).strip() == '':
        existing = MotdOption.query.filter_by(restaurant_id=restaurant.id, weekday=weekday).first()
        if existing:
            db.session.delete(existing)
            db.session.commit()
        return jsonify({'message': 'MOTD cleared', 'weekday': weekday, 'restaurant_id': restaurant.id}), 200

    option_text = str(option_text).strip()
    existing = MotdOption.query.filter_by(restaurant_id=restaurant.id, weekday=weekday).first()
    if existing:
        existing.option_text = option_text
    else:
        db.session.add(MotdOption(restaurant_id=restaurant.id, weekday=weekday, option_text=option_text))
    db.session.commit()
    return jsonify({'message': 'MOTD saved', 'weekday': weekday, 'restaurant_id': restaurant.id, 'option_text': option_text}), 200


@bp.route('/orders/by-date', methods=['GET'])
@admin_required
def get_orders_by_date(user):
    """Get orders for a selected day, grouped by restaurant."""
    target_date = request.args.get('date') or date.today().isoformat()
    try:
        target_date_obj = datetime.strptime(target_date, '%Y-%m-%d').date()
    except Exception:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD.'}), 400

    orders = Order.query.filter(Order.order_date == target_date_obj).order_by(Order.restaurant_id.asc(), Order.created_at.asc()).all()

    by_restaurant: dict[int, list[Order]] = {}
    for o in orders:
        by_restaurant.setdefault(o.restaurant_id, []).append(o)

    groups = []
    if by_restaurant:
        sent_logs = RestaurantOrderEmailLog.query.filter(RestaurantOrderEmailLog.order_date == target_date_obj).all()
        sent_by_restaurant = {l.restaurant_id: l for l in sent_logs}

        restaurants = Restaurant.query.filter(Restaurant.id.in_(list(by_restaurant.keys()))).all()
        restaurant_map = {r.id: r for r in restaurants}
        for rest_id in sorted(by_restaurant.keys()):
            r = restaurant_map.get(rest_id)
            if not r:
                continue
            log_row = sent_by_restaurant.get(r.id)
            groups.append({
                'restaurant': {
                    'id': r.id,
                    'name': r.name,
                    'email': r.email,
                    'contact_name': r.contact_name,
                    'email_sent': log_row is not None,
                    'email_sent_at': log_row.created_at.isoformat() if log_row else None,
                },
                'orders': [o.to_dict(include_items=True) for o in by_restaurant[rest_id]],
            })

    return jsonify({'date': target_date_obj.isoformat(), 'groups': groups}), 200


@bp.route('/orders/email-draft', methods=['POST'])
@admin_required
@validate_json
def get_order_email_draft(user):
    """Build an email draft for a restaurant for a date (no send)."""
    target_date = request.json.get('date') or date.today().isoformat()
    restaurant_id = request.json.get('restaurant_id')
    if not restaurant_id:
        return jsonify({'error': 'restaurant_id is required'}), 400
    try:
        target_date_obj = datetime.strptime(target_date, '%Y-%m-%d').date()
    except Exception:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD.'}), 400

    restaurant = db.session.get(Restaurant, int(restaurant_id))
    if not restaurant:
        return jsonify({'error': 'Restaurant not found'}), 404

    orders = Order.query.filter(Order.order_date == target_date_obj, Order.restaurant_id == restaurant.id).order_by(Order.created_at.asc()).all()
    draft = _build_restaurant_email_draft(target_date_obj, restaurant, orders)
    return jsonify({'draft': draft}), 200


@bp.route('/orders/send-email', methods=['POST'])
@admin_required
@validate_json
def send_order_email(user):
    """Log an email draft for a restaurant for a date (placeholder for real send)."""
    target_date = request.json.get('date') or date.today().isoformat()
    restaurant_id = request.json.get('restaurant_id')
    if not restaurant_id:
        return jsonify({'error': 'restaurant_id is required'}), 400
    try:
        target_date_obj = datetime.strptime(target_date, '%Y-%m-%d').date()
    except Exception:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD.'}), 400

    restaurant = db.session.get(Restaurant, int(restaurant_id))
    if not restaurant:
        return jsonify({'error': 'Restaurant not found'}), 404
    if not restaurant.email:
        return jsonify({'error': 'Restaurant has no email configured'}), 400

    orders = Order.query.filter(Order.order_date == target_date_obj, Order.restaurant_id == restaurant.id).order_by(Order.created_at.asc()).all()
    draft = _build_restaurant_email_draft(target_date_obj, restaurant, orders)

    # Upsert log record (so UI can show "sent")
    existing_log = RestaurantOrderEmailLog.query.filter_by(restaurant_id=restaurant.id, order_date=target_date_obj).first()
    if existing_log is None:
        db.session.add(RestaurantOrderEmailLog(restaurant_id=restaurant.id, order_date=target_date_obj, sent_by_user_id=user.id))

    # Mark involved orders as ordered (so they are closed out in the workflow)
    for o in orders:
        if o.status not in ['cancelled', 'completed']:
            o.status = 'ordered'

    db.session.commit()

    current_app.logger.info(
        "ADMIN_EMAIL_DRAFT to=%s subject=%s\n%s",
        draft.get('to'),
        draft.get('subject'),
        draft.get('body'),
    )
    return jsonify({'message': 'Email logged (not sent).', 'draft': draft}), 200


@bp.route('/orders/send-all-emails', methods=['POST'])
@admin_required
@validate_json
def send_all_order_emails(user):
    """Log email drafts for all restaurants with orders on a date (placeholder for real send)."""
    target_date = request.json.get('date') or date.today().isoformat()
    try:
        target_date_obj = datetime.strptime(target_date, '%Y-%m-%d').date()
    except Exception:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD.'}), 400

    orders = Order.query.filter(Order.order_date == target_date_obj).order_by(Order.restaurant_id.asc(), Order.created_at.asc()).all()
    if not orders:
        return jsonify({'message': 'No orders for this date.', 'sent': 0, 'skipped': []}), 200

    by_restaurant: dict[int, list[Order]] = {}
    for o in orders:
        by_restaurant.setdefault(o.restaurant_id, []).append(o)

    restaurants = Restaurant.query.filter(Restaurant.id.in_(list(by_restaurant.keys()))).all()
    restaurant_map = {r.id: r for r in restaurants}

    sent = 0
    skipped = []
    for rest_id, rest_orders in by_restaurant.items():
        r = restaurant_map.get(rest_id)
        if not r:
            continue
        if not r.email:
            skipped.append({'restaurant_id': r.id, 'restaurant_name': r.name, 'reason': 'Missing email'})
            continue
        draft = _build_restaurant_email_draft(target_date_obj, r, rest_orders)

        existing_log = RestaurantOrderEmailLog.query.filter_by(restaurant_id=r.id, order_date=target_date_obj).first()
        if existing_log is None:
            db.session.add(RestaurantOrderEmailLog(restaurant_id=r.id, order_date=target_date_obj, sent_by_user_id=user.id))

        for o in rest_orders:
            if o.status not in ['cancelled', 'completed']:
                o.status = 'ordered'

        current_app.logger.info(
            "ADMIN_EMAIL_DRAFT to=%s subject=%s\n%s",
            draft.get('to'),
            draft.get('subject'),
            draft.get('body'),
        )
        sent += 1

    db.session.commit()

    return jsonify({'message': 'Emails logged (not sent).', 'sent': sent, 'skipped': skipped}), 200


@bp.route('/restaurants/availability', methods=['GET'])
@admin_required
def get_restaurant_availability(user):
    """Get availability for all restaurants."""
    rows = RestaurantAvailability.query.all()
    by_restaurant = {}
    for r in rows:
        if r.is_available:
            by_restaurant.setdefault(r.restaurant_id, set()).add(r.weekday)
    return jsonify({
        'availability': {str(k): sorted(list(v)) for k, v in by_restaurant.items()}
    }), 200


@bp.route('/restaurants/<int:restaurant_id>/availability', methods=['PUT'])
@admin_required
@validate_json
def set_restaurant_availability(user, restaurant_id):
    """Set availability weekdays for a restaurant. Expects {weekdays:[0-6]}."""
    weekdays = request.json.get('weekdays')
    if weekdays is None or not isinstance(weekdays, list):
        return jsonify({'error': 'weekdays must be a list of integers 0-6'}), 400
    try:
        weekdays = sorted({int(w) for w in weekdays})
    except Exception:
        return jsonify({'error': 'weekdays must be integers 0-6'}), 400
    if any(w < 0 or w > 6 for w in weekdays):
        return jsonify({'error': 'weekdays must be in range 0-6'}), 400

    # Upsert all weekdays so "none selected" still counts as configured.
    existing = {
        row.weekday: row
        for row in RestaurantAvailability.query.filter_by(restaurant_id=restaurant_id).all()
    }
    for w in range(7):
        row = existing.get(w)
        if row is None:
            row = RestaurantAvailability(restaurant_id=restaurant_id, weekday=w, is_available=(w in weekdays))
            db.session.add(row)
        else:
            row.is_available = w in weekdays
    db.session.commit()
    return jsonify({'message': 'Availability updated', 'restaurant_id': restaurant_id, 'weekdays': weekdays}), 200


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
    
    # Orders today (exclude cancelled)
    orders_today = Order.query.filter(
        Order.order_date == today,
        Order.status != 'cancelled'
    ).count()

    pending_orders_today = Order.query.filter(
        Order.order_date == today,
        Order.status == 'pending'
    ).count()
    
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
    
    # Flatten key stats for frontend, keep legacy nested structure too.
    payload = {
        'total_users': total_users,
        'total_orders_today': orders_today,
        'pending_orders': pending_orders_today,
        'pending_orders_today': pending_orders_today,
        'total_revenue_today': 0,
        'stats': {
            'total_users': total_users,
            'total_restaurants': total_restaurants,
            'total_menus': total_menus,
            'orders_this_week': orders_this_week,
            'orders_today': orders_today,
            'pending_orders_today': pending_orders_today,
            'users_without_orders_tomorrow': len(users_without_orders)
        },
        'status_breakdown': status_counts,
        'recent_orders': [order.to_dict() for order in recent_orders]
    }
    return jsonify(payload), 200


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
