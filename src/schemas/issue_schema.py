"""Issue validation schemas."""

from marshmallow import Schema, fields, validate


class IssueCreateSchema(Schema):
    """Schema for creating an issue."""
    title = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=200)
    )
    description = fields.Str(validate=validate.Length(max=5000))
    priority = fields.Str(
        validate=validate.OneOf(['low', 'medium', 'high', 'critical']),
        load_default='medium'
    )
    status = fields.Str(
        validate=validate.OneOf(['open', 'in_progress', 'resolved', 'closed']),
        load_default='open'
    )


class IssueUpdateSchema(Schema):
    """Schema for updating an issue."""
    title = fields.Str(validate=validate.Length(min=1, max=200))
    description = fields.Str(validate=validate.Length(max=5000))
    priority = fields.Str(
        validate=validate.OneOf(['low', 'medium', 'high', 'critical'])
    )
    status = fields.Str(
        validate=validate.OneOf(['open', 'in_progress', 'resolved', 'closed'])
    )


class IssueResponseSchema(Schema):
    """Schema for issue response."""
    id = fields.Int(dump_only=True)
    project_id = fields.Int()
    title = fields.Str()
    description = fields.Str()
    status = fields.Str()
    priority = fields.Str()
    reporter_id = fields.Int()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class IssueAssignmentSchema(Schema):
    """Schema for assigning users to issue."""
    user_id = fields.Int(required=True)
