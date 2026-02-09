"""Restaurant schemas for validation and serialization."""
from marshmallow import Schema, fields, validate


class RestaurantSchema(Schema):
    """Restaurant schema."""
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    contact_name = fields.Str(validate=validate.Length(max=200))
    phone_number = fields.Str(validate=validate.Length(max=20))
    email = fields.Email()
    address = fields.Str()
    is_active = fields.Bool()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class RestaurantCreateSchema(Schema):
    """Schema for creating a restaurant."""
    name = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    contact_name = fields.Str(validate=validate.Length(max=200))
    phone_number = fields.Str(validate=validate.Length(max=20))
    email = fields.Email()
    address = fields.Str()


class RestaurantUpdateSchema(Schema):
    """Schema for updating a restaurant."""
    name = fields.Str(validate=validate.Length(min=1, max=200))
    contact_name = fields.Str(validate=validate.Length(max=200))
    phone_number = fields.Str(validate=validate.Length(max=20))
    email = fields.Email()
    address = fields.Str()
    is_active = fields.Bool()
