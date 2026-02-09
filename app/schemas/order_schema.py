"""Order schemas for validation and serialization."""
from marshmallow import Schema, fields, validate, validates, ValidationError
from datetime import date


class OrderItemSchema(Schema):
    """Order item schema."""
    id = fields.Int(dump_only=True)
    order_id = fields.Int(dump_only=True)
    menu_item_id = fields.Int(required=True)
    menu_item_name = fields.Str(dump_only=True)
    quantity = fields.Int(required=True, validate=validate.Range(min=1))
    price = fields.Decimal(dump_only=True, as_string=True, places=2)
    subtotal = fields.Decimal(dump_only=True, as_string=True, places=2)
    notes = fields.Str()
    created_at = fields.DateTime(dump_only=True)


class OrderItemCreateSchema(Schema):
    """Schema for creating an order item."""
    menu_item_id = fields.Int(required=True)
    quantity = fields.Int(required=True, validate=validate.Range(min=1, max=100))
    notes = fields.Str(validate=validate.Length(max=500))


class OrderSchema(Schema):
    """Order schema."""
    id = fields.Int(dump_only=True)
    user_id = fields.Int(dump_only=True)
    user_name = fields.Str(dump_only=True)
    menu_id = fields.Int(required=True)
    menu_name = fields.Str(dump_only=True)
    restaurant_id = fields.Int(dump_only=True)
    restaurant_name = fields.Str(dump_only=True)
    order_date = fields.Date(required=True)
    status = fields.Str(validate=validate.OneOf(['pending', 'confirmed', 'sent_to_restaurant', 'completed', 'cancelled']))
    total_amount = fields.Decimal(dump_only=True, as_string=True, places=2)
    notes = fields.Str()
    items = fields.List(fields.Nested(OrderItemSchema), dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    
    @validates('order_date')
    def validate_order_date(self, value):
        """Validate order date is not in the past."""
        if isinstance(value, str):
            from datetime import datetime
            value = datetime.strptime(value, '%Y-%m-%d').date()
        if value < date.today():
            raise ValidationError('Order date cannot be in the past')


class OrderCreateSchema(Schema):
    """Schema for creating an order."""
    menu_id = fields.Int(required=True)
    order_date = fields.Date(required=True)
    notes = fields.Str(validate=validate.Length(max=1000))
    items = fields.List(fields.Nested(OrderItemCreateSchema), required=True, validate=validate.Length(min=1))


class OrderUpdateSchema(Schema):
    """Schema for updating an order."""
    notes = fields.Str(validate=validate.Length(max=1000))
    items = fields.List(fields.Nested(OrderItemCreateSchema), validate=validate.Length(min=1))


class OrderStatusUpdateSchema(Schema):
    """Schema for updating order status (admin only)."""
    status = fields.Str(required=True, validate=validate.OneOf(['pending', 'confirmed', 'sent_to_restaurant', 'completed', 'cancelled']))
