"""User validation schemas."""

from marshmallow import Schema, fields, validate, validates, ValidationError
import re


class UserRegistrationSchema(Schema):
    """Schema for user registration."""
    username = fields.Str(
        required=True,
        validate=[
            validate.Length(min=3, max=50),
            validate.Regexp(r'^[a-zA-Z0-9_-]+$', error='Username can only contain letters, numbers, underscores, and hyphens')
        ]
    )
    email = fields.Email(required=True, validate=validate.Length(max=120))
    password = fields.Str(
        required=True,
        validate=validate.Length(min=8, max=128),
        load_only=True
    )
    role = fields.Str(
        validate=validate.OneOf(['admin', 'developer', 'viewer']),
        load_default='developer'
    )
    
    @validates('password')
    def validate_password(self, value):
        """Validate password strength."""
        if not re.search(r'[A-Z]', value):
            raise ValidationError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', value):
            raise ValidationError('Password must contain at least one lowercase letter')
        if not re.search(r'[0-9]', value):
            raise ValidationError('Password must contain at least one digit')


class UserLoginSchema(Schema):
    """Schema for user login."""
    username = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)


class UserUpdateSchema(Schema):
    """Schema for updating user."""
    email = fields.Email(validate=validate.Length(max=120))
    role = fields.Str(validate=validate.OneOf(['admin', 'developer', 'viewer']))
    is_active = fields.Bool()


class UserResponseSchema(Schema):
    """Schema for user response."""
    id = fields.Int(dump_only=True)
    username = fields.Str()
    email = fields.Email()
    role = fields.Str()
    is_active = fields.Bool()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class UserPublicSchema(Schema):
    """Schema for public user info (without email)."""
    id = fields.Int(dump_only=True)
    username = fields.Str()
    role = fields.Str()
    created_at = fields.DateTime(dump_only=True)
