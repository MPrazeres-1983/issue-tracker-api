"""Project routes."""

from flask import Blueprint, request
from marshmallow import ValidationError
from src.services import ProjectService
from src.schemas import ProjectCreateSchema, ProjectUpdateSchema, ProjectResponseSchema, ProjectMemberAddSchema
from src.utils.responses import (
    success_response,
    error_response,
    validation_error_response,
    created_response,
    not_found_response,
    forbidden_response,
    no_content_response,
)
from src.utils.pagination import get_pagination_params, build_pagination_response
from src.middleware import require_auth, get_current_user_id
from src.utils.logger import logger

projects_bp = Blueprint('projects', __name__, url_prefix='/api/v1/projects')
project_service = ProjectService()


@projects_bp.route('', methods=['GET'])
@require_auth
def get_projects():
    """Get all projects for current user with pagination and filters."""
    try:
        user_id = get_current_user_id()
        
        # Get pagination params
        pagination = get_pagination_params()
        page = pagination['page']
        per_page = pagination['per_page']
        
        # Get filters
        owner_id = request.args.get('owner_id', type=int)
        search = request.args.get('search')
        is_active = request.args.get('is_active', type=lambda v: v.lower() == 'true')
        
        # Always scope the query to projects this user can access BEFORE
        # applying optional filters, otherwise owner_id leaks another user's data.
        projects = project_service.get_user_projects(user_id)
        if owner_id is not None:
            projects = [p for p in projects if p.owner_id == owner_id]
        if search:
            projects = [p for p in projects if search.lower() in p.name.lower()]
        if is_active is not None:
            projects = [p for p in projects if p.is_active == is_active]

        total = len(projects)
        start = (page - 1) * per_page
        items = projects[start:start + per_page]

        # Serialize
        schema = ProjectResponseSchema(many=True)
        data = schema.dump(items)
        
        return success_response(
            data=data,
            meta={
                'total': total,
                'page': page,
                'per_page': per_page,
                'total_pages': (total + per_page - 1) // per_page if total > 0 else 0
            }
        )
    
    except Exception as e:
        logger.error(f"Error in get_projects: {str(e)}")
        return error_response("Failed to get projects", status_code=500)


@projects_bp.route('', methods=['POST'])
@require_auth
def create_project():
    """Create a new project."""
    try:
        user_id = get_current_user_id()
        
        # Validate input
        schema = ProjectCreateSchema()
        data = schema.load(request.get_json())
        
        # Create project
        project, error = project_service.create_project(
            name=data['name'],
            owner_id=user_id,
            description=data.get('description')
        )
        
        if error:
            return error_response(error, status_code=400)
        
        # Serialize
        response_schema = ProjectResponseSchema()
        return created_response(
            data=response_schema.dump(project),
            message="Project created successfully"
        )
    
    except ValidationError as e:
        return validation_error_response(e.messages)
    except Exception as e:
        logger.error(f"Error in create_project: {str(e)}")
        return error_response("Failed to create project", status_code=500)


@projects_bp.route('/<int:project_id>', methods=['GET'])
@require_auth
def get_project(project_id):
    """Get project by ID."""
    try:
        user_id = get_current_user_id()
        
        project = project_service.get_project(project_id)
        
        if not project:
            return not_found_response("Project not found")
        
        # Check access
        if not project_service.can_access_project(project_id, user_id):
            return forbidden_response("Access denied")
        
        # Serialize
        schema = ProjectResponseSchema()
        return success_response(data=schema.dump(project))
    
    except Exception as e:
        logger.error(f"Error in get_project: {str(e)}")
        return error_response("Failed to get project", status_code=500)


@projects_bp.route('/<int:project_id>', methods=['PUT'])
@require_auth
def update_project(project_id):
    """Update project."""
    try:
        user_id = get_current_user_id()
        
        # Validate input
        schema = ProjectUpdateSchema()
        data = schema.load(request.get_json())
        
        # Update project
        project, error = project_service.update_project(project_id, user_id, **data)
        
        if error:
            if "not found" in error.lower():
                return not_found_response(error)
            elif "not authorized" in error.lower():
                return forbidden_response(error)
            return error_response(error, status_code=400)
        
        # Serialize
        response_schema = ProjectResponseSchema()
        return success_response(
            data=response_schema.dump(project),
            message="Project updated successfully"
        )
    
    except ValidationError as e:
        return validation_error_response(e.messages)
    except Exception as e:
        logger.error(f"Error in update_project: {str(e)}")
        return error_response("Failed to update project", status_code=500)


@projects_bp.route('/<int:project_id>', methods=['DELETE'])
@require_auth
def delete_project(project_id):
    """Delete project."""
    try:
        user_id = get_current_user_id()
        
        success, error = project_service.delete_project(project_id, user_id)
        
        if error:
            if "not found" in error.lower():
                return not_found_response(error)
            elif "owner" in error.lower() or "admin" in error.lower():
                return forbidden_response(error)
            return error_response(error, status_code=400)
        
        return no_content_response()
    
    except Exception as e:
        logger.error(f"Error in delete_project: {str(e)}")
        return error_response("Failed to delete project", status_code=500)


@projects_bp.route('/<int:project_id>/members', methods=['POST'])
@require_auth
def add_member(project_id):
    """Add member to project."""
    try:
        user_id = get_current_user_id()
        
        # Validate input
        schema = ProjectMemberAddSchema()
        data = schema.load(request.get_json())
        
        # Add member
        success, error = project_service.add_member(
            project_id=project_id,
            user_id=user_id,
            member_user_id=data['user_id'],
            role=data.get('role', 'member')
        )
        
        if error:
            if "not found" in error.lower():
                return not_found_response(error)
            elif "not authorized" in error.lower():
                return forbidden_response(error)
            return error_response(error, status_code=400)
        
        return success_response(message="Member added successfully", status_code=201)
    
    except ValidationError as e:
        return validation_error_response(e.messages)
    except Exception as e:
        logger.error(f"Error in add_member: {str(e)}")
        return error_response("Failed to add member", status_code=500)


@projects_bp.route('/<int:project_id>/members/<int:member_user_id>', methods=['DELETE'])
@require_auth
def remove_member(project_id, member_user_id):
    """Remove member from project."""
    try:
        user_id = get_current_user_id()
        
        success, error = project_service.remove_member(project_id, user_id, member_user_id)
        
        if error:
            if "not found" in error.lower():
                return not_found_response(error)
            elif "not authorized" in error.lower() or "owner" in error.lower():
                return forbidden_response(error)
            return error_response(error, status_code=400)
        
        return no_content_response()
    
    except Exception as e:
        logger.error(f"Error in remove_member: {str(e)}")
        return error_response("Failed to remove member", status_code=500)
