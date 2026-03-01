"""Unit tests for AuthService (refresh, update_password) and utility functions."""

import pytest
from src.services import AuthService


@pytest.mark.unit
class TestAuthServiceRefresh:
    """AuthService.refresh"""

    def test_refresh_success(self, app, db, sample_user):
        service = AuthService()
        identity = {
            'user_id': sample_user.id,
            'username': sample_user.username,
            'role': sample_user.role
        }
        with app.app_context():
            result, error = service.refresh(identity)
        assert result is not None
        assert error is None
        assert 'access_token' in result

    def test_refresh_user_not_found(self, app, db):
        service = AuthService()
        identity = {'user_id': 99999, 'username': 'ghost', 'role': 'developer'}
        with app.app_context():
            result, error = service.refresh(identity)
        assert result is None
        assert 'not found' in error.lower()


@pytest.mark.unit
class TestAuthServiceUpdatePassword:
    """AuthService.update_password"""

    def test_update_password_success(self, db, sample_user):
        service = AuthService()
        success, error = service.update_password(
            user_id=sample_user.id,
            current_password='TestPass123!',
            new_password='NewPass456!'
        )
        assert success is True
        assert error is None

    def test_update_password_wrong_current(self, db, sample_user):
        service = AuthService()
        success, error = service.update_password(
            user_id=sample_user.id,
            current_password='WrongPass!',
            new_password='NewPass456!'
        )
        assert success is False
        assert 'incorrect' in error.lower()

    def test_update_password_user_not_found(self, db):
        service = AuthService()
        success, error = service.update_password(
            user_id=99999,
            current_password='any',
            new_password='new'
        )
        assert success is False
        assert 'not found' in error.lower()


@pytest.mark.unit
class TestAuthServiceGetCurrentUser:
    """AuthService.get_current_user"""

    def test_get_current_user_success(self, db, sample_user):
        service = AuthService()
        user = service.get_current_user(sample_user.id)
        assert user is not None
        assert user.id == sample_user.id

    def test_get_current_user_not_found(self, db):
        service = AuthService()
        user = service.get_current_user(99999)
        assert user is None


@pytest.mark.unit
class TestLoginDisabledUser:
    """AuthService.login — edge case: disabled user"""

    def test_login_disabled_account(self, db):
        """Registering and then manually deactivating a user."""
        service = AuthService()
        user, _ = service.register(
            username='disableduser',
            email='disabled@example.com',
            password='Pass123!',
            role='developer'
        )
        # Deactivate directly via repository
        from src.repositories import UserRepository
        repo = UserRepository()
        repo.update(user.id, is_active=False)

        result, error = service.login(username='disableduser', password='Pass123!')
        assert result is None
        assert error == 'Account is disabled'


@pytest.mark.unit
class TestUtilsResponses:
    """src.utils.responses helpers"""

    def test_success_response_structure(self, app):
        from src.utils.responses import success_response
        with app.app_context():
            body, status = success_response(data={'key': 'val'}, message='OK')
        assert status == 200
        assert body['data'] == {'key': 'val'}
        assert body['message'] == 'OK'

    def test_error_response_structure(self, app):
        from src.utils.responses import error_response
        with app.app_context():
            body, status = error_response('Something went wrong', status_code=400)
        assert status == 400
        assert 'error' in body
        assert body['error']['message'] == 'Something went wrong'

    def test_validation_error_response(self, app):
        from src.utils.responses import validation_error_response
        with app.app_context():
            body, status = validation_error_response({'field': ['required']})
        assert status == 422
        assert body['error']['code'] == 'VALIDATION_ERROR'

    def test_no_content_response(self, app):
        from src.utils.responses import no_content_response
        with app.app_context():
            body, status = no_content_response()
        assert status == 204
        assert body == ''

    def test_not_found_response(self, app):
        from src.utils.responses import not_found_response
        with app.app_context():
            body, status = not_found_response('Item not found')
        assert status == 404

    def test_forbidden_response(self, app):
        from src.utils.responses import forbidden_response
        with app.app_context():
            body, status = forbidden_response()
        assert status == 403


@pytest.mark.unit
class TestUtilsPagination:
    """src.utils.pagination helpers"""

    def test_pagination_class(self, app):
        from src.utils.pagination import Pagination
        p = Pagination(items=[1, 2, 3], total=30, page=2, per_page=10)
        assert p.total_pages == 3
        assert p.has_prev is True
        assert p.has_next is True

    def test_pagination_first_page(self, app):
        from src.utils.pagination import Pagination
        p = Pagination(items=[1], total=5, page=1, per_page=10)
        assert p.has_prev is False
        assert p.has_next is False

    def test_pagination_to_dict(self, app):
        from src.utils.pagination import Pagination
        p = Pagination(items=[], total=0, page=1, per_page=20)
        d = p.to_dict()
        assert 'total' in d
        assert 'page' in d
        assert 'per_page' in d
        assert 'total_pages' in d

    def test_build_pagination_response(self, app):
        from src.utils.pagination import build_pagination_response
        with app.app_context():
            result = build_pagination_response(
                items=[1, 2], total=50, page=2, per_page=10
            )
        assert result['meta']['total'] == 50
        assert result['meta']['has_prev'] is True
        assert result['meta']['has_next'] is True
