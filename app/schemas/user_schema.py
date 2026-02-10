"""User schemas for validation and serialization."""
from marshmallow import Schema, fields, validate, validates, validates_schema, ValidationError
from app.utils.validators import validate_email, validate_phone


class UserSchema(Schema):
    """User schema."""
    id = fields.Int(dump_only=True)
    username = fields.Str(allow_none=True, validate=validate.Length(min=1, max=80))
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True, validate=validate.Length(min=8))
    first_name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    last_name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    full_name = fields.Str(dump_only=True)
    phone_number = fields.Str(validate=validate.Length(max=20))
    birth_date = fields.Date(allow_none=True)
    role = fields.Str(validate=validate.OneOf(['user', 'admin']))
    is_active = fields.Bool()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    
    @validates('phone_number')
    def validate_phone(self, value):
        """Validate phone number format."""
        if value and not validate_phone(value):
            raise ValidationError('Invalid phone number format')


class UserCreateSchema(Schema):
    """Schema for creating a user."""
    username = fields.Str(allow_none=True, validate=validate.Length(min=1, max=80))
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=8))
    first_name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    last_name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    phone_number = fields.Str(validate=validate.Length(max=20))
    birth_date = fields.Date(allow_none=True)
    role = fields.Str(validate=validate.OneOf(['user', 'admin']), load_default='user')


class UserUpdateSchema(Schema):
    """Schema for updating a user."""
    username = fields.Str(allow_none=True, validate=validate.Length(min=1, max=80))
    first_name = fields.Str(validate=validate.Length(min=1, max=100))
    last_name = fields.Str(validate=validate.Length(min=1, max=100))
    phone_number = fields.Str(validate=validate.Length(max=20), allow_none=True)
    is_active = fields.Bool()
    role = fields.Str(validate=validate.OneOf(['user', 'admin']))
    birth_date = fields.Date(allow_none=True)


class LoginSchema(Schema):
    """Schema for login request."""
    # Backwards compat: frontend used to send `email`; we now also accept `identifier`.
    identifier = fields.Str(load_default=None, allow_none=True)
    email = fields.Str(load_default=None, allow_none=True)
    username = fields.Str(load_default=None, allow_none=True)
    password = fields.Str(required=True)

    @validates_schema
    def validate_identifier(self, data, **kwargs):
        identifier = data.get('identifier') or data.get('email') or data.get('username')
        if not identifier:
            raise ValidationError({'identifier': ['Email or username is required.']})


class ChangePasswordSchema(Schema):
    """Schema for changing password."""
    current_password = fields.Str(required=True)
    new_password = fields.Str(required=True, validate=validate.Length(min=8))
