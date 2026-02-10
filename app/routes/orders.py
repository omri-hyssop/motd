"""Order routes."""
from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from datetime import datetime
from app.services.order_service import OrderService
from app.schemas import OrderSchema, OrderCreateSchema, OrderUpdateSchema, SimpleOrderCreateSchema, SimpleOrderUpdateSchema
from app.middleware.auth import auth_required
from app.utils.decorators import validate_json

bp = Blueprint('orders', __name__, url_prefix='/api/orders')

order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)
order_create_schema = OrderCreateSchema()
order_update_schema = OrderUpdateSchema()
simple_order_create_schema = SimpleOrderCreateSchema()
simple_order_update_schema = SimpleOrderUpdateSchema()


@bp.route('', methods=['GET'])
@auth_required
def list_orders(user):
    """Get user's orders with optional filters."""
    # Get query parameters
    status = request.args.get('status')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    
    # Parse dates if provided
    if date_from:
        date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
    if date_to:
        date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
    
    # Get orders
    orders = OrderService.get_user_orders(
        user_id=user.id,
        status=status,
        date_from=date_from,
        date_to=date_to
    )
    
    # Use model serialization so dump_only fields (restaurant_name, etc) are populated.
    return jsonify({'orders': [o.to_dict(include_items=True) for o in orders]}), 200


@bp.route('', methods=['POST'])
@auth_required
@validate_json
def create_order(user):
    """Create a new order."""
    try:
        # Validate input
        data = order_create_schema.load(request.json)
        
        # Create order
        order = OrderService.create_order(
            user_id=user.id,
            menu_id=data['menu_id'],
            order_date=data['order_date'],
            items_data=data['items'],
            notes=data.get('notes')
        )
        
        return jsonify({
            'message': 'Order created successfully',
            'order': order.to_dict(include_items=True)
        }), 201
        
    except ValidationError as e:
        return jsonify({'error': 'Validation error', 'messages': e.messages}), 400
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@bp.route('/simple', methods=['POST'])
@auth_required
@validate_json
def create_simple_order(user):
    """Create a new freeform order (Mon-Fri only)."""
    try:
        data = simple_order_create_schema.load(request.json)
        order = OrderService.create_simple_order(
            user_id=user.id,
            restaurant_id=data['restaurant_id'],
            order_date=data['order_date'],
            order_text=data['order_text'],
            notes=data.get('notes'),
        )
        return jsonify({'message': 'Order created successfully', 'order': order.to_dict(include_items=True)}), 201
    except ValidationError as e:
        return jsonify({'error': 'Validation error', 'messages': e.messages}), 400
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@bp.route('/<int:order_id>/simple', methods=['PUT'])
@auth_required
@validate_json
def update_simple_order(user, order_id):
    """Update a freeform order (pending only)."""
    try:
        data = simple_order_update_schema.load(request.json)
        order = OrderService.update_simple_order(
            order_id=order_id,
            user_id=user.id,
            restaurant_id=data['restaurant_id'],
            order_text=data['order_text'],
            notes=data.get('notes'),
        )
        return jsonify({'message': 'Order updated successfully', 'order': order.to_dict(include_items=True)}), 200
    except ValidationError as e:
        return jsonify({'error': 'Validation error', 'messages': e.messages}), 400
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@bp.route('/<int:order_id>', methods=['GET'])
@auth_required
def get_order(user, order_id):
    """Get order details."""
    from app.models import Order
    
    order = Order.query.filter_by(id=order_id, user_id=user.id).first()
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    
    return jsonify(order.to_dict(include_items=True)), 200


@bp.route('/<int:order_id>', methods=['PUT'])
@auth_required
@validate_json
def update_order(user, order_id):
    """Update an order (only pending orders)."""
    try:
        # Validate input
        data = order_update_schema.load(request.json)
        
        # Update order
        order = OrderService.update_order(
            order_id=order_id,
            user_id=user.id,
            items_data=data.get('items'),
            notes=data.get('notes')
        )
        
        return jsonify({
            'message': 'Order updated successfully',
            'order': order.to_dict(include_items=True)
        }), 200
        
    except ValidationError as e:
        return jsonify({'error': 'Validation error', 'messages': e.messages}), 400
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@bp.route('/<int:order_id>', methods=['DELETE'])
@auth_required
def cancel_order(user, order_id):
    """Cancel an order."""
    try:
        order = OrderService.cancel_order(order_id, user.id)
        
        return jsonify({
            'message': 'Order cancelled successfully',
            'order': order_schema.dump(order)
        }), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@bp.route('/week', methods=['GET'])
@auth_required
def get_weekly_orders(user):
    """Get weekly order calendar."""
    # Get start date from query params (default to today)
    start_date = request.args.get('start_date')
    
    weekly_data = OrderService.get_weekly_orders(user.id, start_date)
    
    return jsonify({
        'weekly_orders': weekly_data
    }), 200


@bp.route('/missing-days', methods=['GET'])
@auth_required
def get_missing_days(user):
    """Get dates where user hasn't ordered yet."""
    # Get parameters
    days_ahead = int(request.args.get('days_ahead', 7))
    start_date = request.args.get('start_date')
    
    missing_dates = OrderService.get_missing_order_days(
        user_id=user.id,
        days_ahead=days_ahead,
        start_date=start_date
    )
    
    return jsonify({
        'missing_dates': [d.isoformat() for d in missing_dates],
        'count': len(missing_dates)
    }), 200
