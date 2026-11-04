"""Integration tests for project routes."""

import pytest


@pytest.mark.integration
class TestGetProjects:
    """GET /api/v1/projects"""

    def test_list_projects_authenticated(self, client, auth_headers, sample_project):
        response = client.get('/api/v1/projects', headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert 'data' in data

    def test_list_projects_unauthenticated(self, client):
        response = client.get('/api/v1/projects')
        assert response.status_code == 401

    def test_list_projects_returns_meta(self, client, auth_headers, sample_project):
        response = client.get('/api/v1/projects', headers=auth_headers)
        data = response.get_json()
        assert 'meta' in data
        assert 'total' in data['meta']


    def test_owner_filter_cannot_list_another_users_projects(self, client, second_user_headers, sample_project):
        """An owner_id filter must not bypass project membership checks."""
        response = client.get(
            f'/api/v1/projects?owner_id={sample_project.owner_id}',
            headers=second_user_headers,
        )
        assert response.status_code == 200
        assert response.get_json()['meta']['total'] == 0
        assert response.get_json()['data'] == []

    def test_search_is_scoped_to_accessible_projects(self, client, second_user_headers, sample_project):
        response = client.get(
            f'/api/v1/projects?search={sample_project.name}',
            headers=second_user_headers,
        )
        assert response.status_code == 200
        assert response.get_json()['data'] == []

    def test_list_projects_pagination(self, client, auth_headers, sample_project):
        response = client.get('/api/v1/projects?page=1&per_page=5', headers=auth_headers)
        assert response.status_code == 200


@pytest.mark.integration
class TestCreateProject:
    """POST /api/v1/projects"""

    def test_create_project_success(self, client, auth_headers):
        response = client.post('/api/v1/projects', headers=auth_headers, json={
            'name': 'New Project',
            'description': 'A brand new project'
        })
        assert response.status_code == 201
        data = response.get_json()
        assert data['data']['name'] == 'New Project'

    def test_create_project_without_description(self, client, auth_headers):
        response = client.post('/api/v1/projects', headers=auth_headers, json={
            'name': 'Minimal Project'
        })
        assert response.status_code == 201

    def test_create_project_missing_name(self, client, auth_headers):
        response = client.post('/api/v1/projects', headers=auth_headers, json={
            'description': 'No name provided'
        })
        assert response.status_code == 422

    def test_create_project_unauthenticated(self, client):
        response = client.post('/api/v1/projects', json={'name': 'Unauthorized'})
        assert response.status_code == 401


@pytest.mark.integration
class TestGetProject:
    """GET /api/v1/projects/<id>"""

    def test_get_project_success(self, client, auth_headers, sample_project):
        response = client.get(
            f'/api/v1/projects/{sample_project.id}',
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['id'] == sample_project.id
        assert data['data']['name'] == 'Test Project'

    def test_get_project_not_found(self, client, auth_headers):
        response = client.get('/api/v1/projects/99999', headers=auth_headers)
        assert response.status_code == 404

    def test_get_project_unauthenticated(self, client, sample_project):
        response = client.get(f'/api/v1/projects/{sample_project.id}')
        assert response.status_code == 401

    def test_get_project_no_access(self, client, second_user_headers, sample_project):
        """A user who is not a member of the project cannot access it."""
        response = client.get(
            f'/api/v1/projects/{sample_project.id}',
            headers=second_user_headers
        )
        assert response.status_code == 403


@pytest.mark.integration
class TestUpdateProject:
    """PUT /api/v1/projects/<id>"""

    def test_update_project_success(self, client, auth_headers, sample_project):
        response = client.put(
            f'/api/v1/projects/{sample_project.id}',
            headers=auth_headers,
            json={'name': 'Updated Name', 'description': 'Updated desc'}
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['name'] == 'Updated Name'

    def test_update_project_not_found(self, client, auth_headers):
        response = client.put(
            '/api/v1/projects/99999',
            headers=auth_headers,
            json={'name': 'Ghost'}
        )
        assert response.status_code == 404

    def test_update_project_forbidden(self, client, second_user_headers, sample_project):
        response = client.put(
            f'/api/v1/projects/{sample_project.id}',
            headers=second_user_headers,
            json={'name': 'Hijacked'}
        )
        # second_user is not a member, so either 403 or 404 is acceptable
        assert response.status_code in (403, 404)

    def test_update_project_unauthenticated(self, client, sample_project):
        response = client.put(
            f'/api/v1/projects/{sample_project.id}',
            json={'name': 'No auth'}
        )
        assert response.status_code == 401


@pytest.mark.integration
class TestDeleteProject:
    """DELETE /api/v1/projects/<id>"""

    def test_delete_project_success(self, client, auth_headers, sample_user):
        # Create a dedicated project to delete
        create_resp = client.post('/api/v1/projects', headers=auth_headers, json={
            'name': 'To Delete'
        })
        project_id = create_resp.get_json()['data']['id']

        response = client.delete(
            f'/api/v1/projects/{project_id}',
            headers=auth_headers
        )
        assert response.status_code == 204

    def test_delete_project_not_found(self, client, auth_headers):
        response = client.delete('/api/v1/projects/99999', headers=auth_headers)
        assert response.status_code == 404

    def test_delete_project_forbidden(self, client, second_user_headers, sample_project):
        response = client.delete(
            f'/api/v1/projects/{sample_project.id}',
            headers=second_user_headers
        )
        assert response.status_code in (403, 404)

    def test_delete_project_unauthenticated(self, client, sample_project):
        response = client.delete(f'/api/v1/projects/{sample_project.id}')
        assert response.status_code == 401


@pytest.mark.integration
class TestProjectMembers:
    """POST/DELETE /api/v1/projects/<id>/members"""

    def test_add_member_success(self, client, auth_headers, sample_project, second_user):
        response = client.post(
            f'/api/v1/projects/{sample_project.id}/members',
            headers=auth_headers,
            json={'user_id': second_user.id, 'role': 'member'}
        )
        assert response.status_code == 201

    def test_add_member_already_member(self, client, auth_headers, sample_project, sample_user):
        """Owner is already a member — should return 400."""
        response = client.post(
            f'/api/v1/projects/{sample_project.id}/members',
            headers=auth_headers,
            json={'user_id': sample_user.id, 'role': 'member'}
        )
        assert response.status_code == 400

    def test_add_member_user_not_found(self, client, auth_headers, sample_project):
        response = client.post(
            f'/api/v1/projects/{sample_project.id}/members',
            headers=auth_headers,
            json={'user_id': 99999, 'role': 'member'}
        )
        assert response.status_code == 404

    def test_add_member_forbidden(self, client, second_user_headers, sample_project, second_user):
        response = client.post(
            f'/api/v1/projects/{sample_project.id}/members',
            headers=second_user_headers,
            json={'user_id': second_user.id, 'role': 'member'}
        )
        assert response.status_code in (403, 404)

    def test_remove_member_success(self, client, auth_headers, sample_project, second_user):
        # First add
        client.post(
            f'/api/v1/projects/{sample_project.id}/members',
            headers=auth_headers,
            json={'user_id': second_user.id, 'role': 'member'}
        )
        # Then remove
        response = client.delete(
            f'/api/v1/projects/{sample_project.id}/members/{second_user.id}',
            headers=auth_headers
        )
        assert response.status_code == 204

    def test_remove_owner_forbidden(self, client, auth_headers, sample_project, sample_user):
        response = client.delete(
            f'/api/v1/projects/{sample_project.id}/members/{sample_user.id}',
            headers=auth_headers
        )
        assert response.status_code == 403
