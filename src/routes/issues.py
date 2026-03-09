"""Issue routes."""

from flask import Blueprint, request
from marshmallow import ValidationError
from src.services import IssueService
from src.schemas import IssueCreateSchema, IssueUpdateSchema, IssueResponseSchema, IssueAssignmentSchema
from src.utils.responses import (
    success_response, error_response, validation_error_response, created_response,
    not_found_response, forbidden_response, no_content_response,
)
from src.utils.pagination import get_pagination_params
from src.middleware import require_auth, get_current_user_id
from src.utils.logger import logger

issues_bp = Blueprint('issues', __name__, url_prefix='/api/v1')
issue_service = IssueService()


@issues_bp.route('/projects/<int:project_id>/issues', methods=['GET'])
@require_auth
def get_issues(project_id):
    """Get issues for a project with pagination and filters."""
    try:
        user_id = get_current_user_id()
        
        # Check access
        from src.services import ProjectService
        project_service = ProjectService()
        if not project_service.can_access_project(project_id, user_id):
            return forbidden_response("Access denied")
        
        # Get pagination
        pagination = get_pagination_params()
        
        # Get filters
        status = request.args.get('status')
        priority = request.args.get('priority')
        reporter_id = request.args.get('reporter_id', type=int)
        assignee_id = request.args.get('assignee_id', type=int)
        search = request.args.get('search')
        
        # Get issues
        from src.repositories import IssueRepository
        repo = IssueRepository()
        result = repo.paginate_with_filters(
            project_id=project_id,
            page=pagination['page'],
            per_page=pagination['per_page'],
            status=status,
            priority=priority,
            reporter_id=reporter_id,
            assignee_id=assignee_id,
            search=search
        )
        
        # Serialize
        schema = IssueResponseSchema(many=True)
        data = schema.dump(result['items'])
        
        return success_response(
            data=data,
            meta={
                'total': result['total'],
                'page': result['page'],
                'per_page': result['per_page'],
                'total_pages': result['total_pages']
            }
        )
    
    except Exception as e:
        logger.error(f"Error in get_issues: {str(e)}")
        return error_response("Failed to get issues", status_code=500)


@issues_bp.route('/projects/<int:project_id>/issues', methods=['POST'])
@require_auth
def create_issue(project_id):
    """Create a new issue."""
    try:
        user_id = get_current_user_id()
        
        schema = IssueCreateSchema()
        data = schema.load(request.get_json())
        
        issue, error = issue_service.create_issue(
            project_id=project_id,
            title=data['title'],
            reporter_id=user_id,
            description=data.get('description'),
            priority=data.get('priority', 'medium'),
            status=data.get('status', 'open')
        )
        
        if error:
            if "not found" in error.lower():
                return not_found_response(error)
            elif "not a member" in error.lower():
                return forbidden_response(error)
            return error_response(error, status_code=400)
        
        response_schema = IssueResponseSchema()
        return created_response(data=response_schema.dump(issue))
    
    except ValidationError as e:
        return validation_error_response(e.messages)
    except Exception as e:
        logger.error(f"Error in create_issue: {str(e)}")
        return error_response("Failed to create issue", status_code=500)


@issues_bp.route('/issues/<int:issue_id>', methods=['GET'])
@require_auth
def get_issue(issue_id):
    """Get issue by ID."""
    try:
        user_id = get_current_user_id()
        
        issue = issue_service.get_issue(issue_id)
        if not issue:
            return not_found_response("Issue not found")
        
        if not issue_service.can_access_issue(issue_id, user_id):
            return forbidden_response("Access denied")
        
        schema = IssueResponseSchema()
        return success_response(data=schema.dump(issue))
    
    except Exception as e:
        logger.error(f"Error in get_issue: {str(e)}")
        return error_response("Failed to get issue", status_code=500)


@issues_bp.route('/issues/<int:issue_id>', methods=['PUT'])
@require_auth
def update_issue(issue_id):
    """Update issue."""
    try:
        user_id = get_current_user_id()
        
        schema = IssueUpdateSchema()
        data = schema.load(request.get_json())
        
        issue, error = issue_service.update_issue(issue_id, user_id, **data)
        
        if error:
            if "not found" in error.lower():
                return not_found_response(error)
            elif "not authorized" in error.lower():
                return forbidden_response(error)
            return error_response(error, status_code=400)
        
        response_schema = IssueResponseSchema()
        return success_response(data=response_schema.dump(issue))
    
    except ValidationError as e:
        return validation_error_response(e.messages)
    except Exception as e:
        logger.error(f"Error in update_issue: {str(e)}")
        return error_response("Failed to update issue", status_code=500)


@issues_bp.route('/issues/<int:issue_id>', methods=['DELETE'])
@require_auth
def delete_issue(issue_id):
    """Delete issue."""
    try:
        user_id = get_current_user_id()
        
        success, error = issue_service.delete_issue(issue_id, user_id)
        
        if error:
            if "not found" in error.lower():
                return not_found_response(error)
            elif "not authorized" in error.lower():
                return forbidden_response(error)
            return error_response(error, status_code=400)
        
        return no_content_response()
    
    except Exception as e:
        logger.error(f"Error in delete_issue: {str(e)}")
        return error_response("Failed to delete issue", status_code=500)


@issues_bp.route('/issues/<int:issue_id>/assign', methods=['POST'])
@require_auth
def assign_user(issue_id):
    """Assign user to issue."""
    try:
        user_id = get_current_user_id()
        
        schema = IssueAssignmentSchema()
        data = schema.load(request.get_json())
        
        success, error = issue_service.assign_user(issue_id, user_id, data['user_id'])
        
        if error:
            if "not found" in error.lower():
                return not_found_response(error)
            elif "not authorized" in error.lower() or "not a member" in error.lower():
                return forbidden_response(error)
            return error_response(error, status_code=400)
        
        return success_response(message="User assigned successfully", status_code=201)
    
    except ValidationError as e:
        return validation_error_response(e.messages)
    except Exception as e:
        logger.error(f"Error in assign_user: {str(e)}")
        return error_response("Failed to assign user", status_code=500)


@issues_bp.route('/issues/<int:issue_id>/assign/<int:assignee_id>', methods=['DELETE'])
@require_auth
def unassign_user(issue_id, assignee_id):
    """Unassign user from issue."""
    try:
        user_id = get_current_user_id()
        
        success, error = issue_service.unassign_user(issue_id, user_id, assignee_id)
        
        if error:
            if "not found" in error.lower():
                return not_found_response(error)
            elif "not authorized" in error.lower():
                return forbidden_response(error)
            return error_response(error, status_code=400)
        
        return no_content_response()
    
    except Exception as e:
        logger.error(f"Error in unassign_user: {str(e)}")
        return error_response("Failed to unassign user", status_code=500)


@issues_bp.route('/issues/<int:issue_id>/labels', methods=['POST'])
@require_auth
def add_label(issue_id):
    """Add label to issue."""
    try:
        user_id = get_current_user_id()
        
        from src.schemas import LabelAssignmentSchema
        schema = LabelAssignmentSchema()
        data = schema.load(request.get_json())
        
        success, error = issue_service.add_label(issue_id, user_id, data['label_id'])
        
        if error:
            if "not found" in error.lower():
                return not_found_response(error)
            elif "not authorized" in error.lower():
                return forbidden_response(error)
            return error_response(error, status_code=400)
        
        return success_response(message="Label added successfully", status_code=201)
    
    except ValidationError as e:
        return validation_error_response(e.messages)
    except Exception as e:
        logger.error(f"Error in add_label: {str(e)}")
        return error_response("Failed to add label", status_code=500)


@issues_bp.route('/issues/suggest', methods=['POST'])
@require_auth
def suggest_issue():
    """Suggest priority and status for an issue using AI classification."""
    try:
        from marshmallow import Schema, fields, validate

        class SuggestSchema(Schema):
            title = fields.Str(required=True, validate=validate.Length(min=1, max=200))
            description = fields.Str(load_default=None)

        schema = SuggestSchema()
        data = schema.load(request.get_json() or {})

        from src.services.suggest_service import SuggestService
        suggest_service = SuggestService()

        suggestion, error = suggest_service.suggest(
            title=data["title"],
            description=data.get("description"),
        )

        if error:
            return error_response(error, status_code=503)

        return success_response(data=suggestion)

    except ValidationError as e:
        return validation_error_response(e.messages)
    except Exception as e:
        logger.error(f"Error in suggest_issue: {str(e)}")
        return error_response("Failed to generate suggestion", status_code=500)
    
@issues_bp.route('/issues/<int:issue_id>/labels/<int:label_id>', methods=['DELETE'])
@require_auth
def remove_label(issue_id, label_id):
    """Remove label from issue."""
    try:
        user_id = get_current_user_id()
        
        success, error = issue_service.remove_label(issue_id, user_id, label_id)
        
        if error:
            if "not found" in error.lower():
                return not_found_response(error)
            elif "not authorized" in error.lower():
                return forbidden_response(error)
            return error_response(error, status_code=400)
        
        return no_content_response()
    
    except Exception as e:
        logger.error(f"Error in remove_label: {str(e)}")
        return error_response("Failed to remove label", status_code=500)
