"""Label validation schemas."""

from marshmallow import Schema, fields, validate, validates, ValidationError
import re


class LabelCreateSchema(Schema):
    """Schema for creating a label."""
    name = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=50)
    )
    color = fields.Str(
        validate=validate.Length(equal=7),
        load_default='#808080'
    )
    
    @validates('color')
    def validate_color(self, value):
        """Validate hex color format."""
        if not re.match(r'^#[0-9A-Fa-f]{6}$', value):
            raise ValidationError('Color must be a valid hex color code (e.g., #FF0000)')


class LabelUpdateSchema(Schema):
    """Schema for updating a label."""
    name = fields.Str(validate=validate.Length(min=1, max=50))
    color = fields.Str(validate=validate.Length(equal=7))
    
    @validates('color')
    def validate_color(self, value):
        """Validate hex color format."""
        if not re.match(r'^#[0-9A-Fa-f]{6}$', value):
            raise ValidationError('Color must be a valid hex color code (e.g., #FF0000)')


class LabelResponseSchema(Schema):
    """Schema for label response."""
    id = fields.Int(dump_only=True)
    name = fields.Str()
    color = fields.Str()
    created_at = fields.DateTime(dump_only=True)


class LabelAssignmentSchema(Schema):
    """Schema for assigning labels to issue."""
    label_id = fields.Int(required=True)
