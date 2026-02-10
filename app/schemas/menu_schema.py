"""Menu and MenuItem schemas for validation and serialization."""
from marshmallow import Schema, fields, validate, validates, ValidationError
from datetime import date


class MenuItemSchema(Schema):
    """Menu item schema."""
    id = fields.Int(dump_only=True)
    menu_id = fields.Int(required=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    description = fields.Str()
    price = fields.Decimal(required=True, as_string=True, places=2)
    dietary_info = fields.Str(validate=validate.Length(max=200))
    image_url = fields.Str(validate=validate.Length(max=500))
    is_available = fields.Bool()
    display_order = fields.Int()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    
    @validates('price')
    def validate_price(self, value):
        """Validate price is positive."""
        if float(value) <= 0:
            raise ValidationError('Price must be positive')


class MenuItemCreateSchema(Schema):
    """Schema for creating a menu item."""
    name = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    description = fields.Str()
    price = fields.Decimal(required=True, as_string=True, places=2)
    dietary_info = fields.Str(validate=validate.Length(max=200))
    image_url = fields.Str(validate=validate.Length(max=500))
    is_available = fields.Bool(load_default=True)
    display_order = fields.Int(load_default=0)


class MenuItemUpdateSchema(Schema):
    """Schema for updating a menu item."""
    name = fields.Str(validate=validate.Length(min=1, max=200))
    description = fields.Str()
    price = fields.Decimal(as_string=True, places=2)
    dietary_info = fields.Str(validate=validate.Length(max=200))
    image_url = fields.Str(validate=validate.Length(max=500))
    is_available = fields.Bool()
    display_order = fields.Int()


class MenuSchema(Schema):
    """Menu schema."""
    id = fields.Int(dump_only=True)
    restaurant_id = fields.Int(required=True)
    restaurant_name = fields.Str(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    description = fields.Str()
    menu_text = fields.Str()
    menu_file_url = fields.Method("get_menu_file_url", dump_only=True)
    menu_file_mime = fields.Str(dump_only=True)
    menu_file_name = fields.Str(dump_only=True)
    available_from = fields.Date(required=True)
    available_until = fields.Date(required=True)
    is_active = fields.Bool()
    items = fields.List(fields.Nested(MenuItemSchema), dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    
    @validates('available_from')
    def validate_available_from(self, value):
        """Validate available_from is not in the past."""
        if isinstance(value, str):
            from datetime import datetime
            value = datetime.strptime(value, '%Y-%m-%d').date()
        # Allow today or future dates
        if value < date.today():
            raise ValidationError('Menu availability date cannot be in the past')

    def get_menu_file_url(self, obj):
        if getattr(obj, "menu_file_path", None):
            return f"/api/uploads/{obj.menu_file_path}"
        return None


class MenuCreateSchema(Schema):
    """Schema for creating a menu."""
    restaurant_id = fields.Int(required=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    description = fields.Str()
    available_from = fields.Date(required=True)
    available_until = fields.Date(required=True)


class MenuUpdateSchema(Schema):
    """Schema for updating a menu."""
    name = fields.Str(validate=validate.Length(min=1, max=200))
    description = fields.Str()
    available_from = fields.Date()
    available_until = fields.Date()
    is_active = fields.Bool()
