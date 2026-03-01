"""Project validation schemas."""

from marshmallow import Schema, fields, validate


class ProjectCreateSchema(Schema):
    """Schema for creating a project."""
    name = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=100)
    )
    description = fields.Str(validate=validate.Length(max=2000))


class ProjectUpdateSchema(Schema):
    """Schema for updating a project."""
    name = fields.Str(validate=validate.Length(min=1, max=100))
    description = fields.Str(validate=validate.Length(max=2000))
    is_active = fields.Bool()


class ProjectResponseSchema(Schema):
    """Schema for project response."""
    id = fields.Int(dump_only=True)
    name = fields.Str()
    description = fields.Str()
    owner_id = fields.Int()
    is_active = fields.Bool()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class ProjectMemberAddSchema(Schema):
    """Schema for adding a project member."""
    user_id = fields.Int(required=True)
    role = fields.Str(
        validate=validate.OneOf(['owner', 'admin', 'member', 'viewer']),
        load_default='member'
    )


class ProjectMemberResponseSchema(Schema):
    """Schema for project member response."""
    id = fields.Int(dump_only=True)
    project_id = fields.Int()
    user_id = fields.Int()
    role = fields.Str()
    joined_at = fields.DateTime(dump_only=True)
