"""Unit tests for ProjectService."""

import pytest
from src.services import ProjectService


@pytest.mark.unit
class TestProjectServiceCreate:
    """ProjectService.create_project"""

    def test_create_project_success(self, db, sample_user):
        service = ProjectService()
        project, error = service.create_project(
            name='My Project',
            owner_id=sample_user.id,
            description='A project'
        )
        assert project is not None
        assert error is None
        assert project.name == 'My Project'
        assert project.owner_id == sample_user.id

    def test_create_project_owner_not_found(self, db):
        service = ProjectService()
        project, error = service.create_project(
            name='Ghost',
            owner_id=99999
        )
        assert project is None
        assert error == 'Owner not found'

    def test_create_project_owner_added_as_member(self, db, sample_user):
        service = ProjectService()
        project, _ = service.create_project(
            name='AutoMember',
            owner_id=sample_user.id
        )
        assert service.can_access_project(project.id, sample_user.id) is True


@pytest.mark.unit
class TestProjectServiceAccess:
    """ProjectService authorization helpers"""

    def test_owner_can_modify(self, db, sample_project, sample_user):
        service = ProjectService()
        assert service.can_modify_project(sample_project.id, sample_user.id) is True

    def test_non_member_cannot_modify(self, db, sample_project, second_user):
        service = ProjectService()
        assert service.can_modify_project(sample_project.id, second_user.id) is False

    def test_owner_can_access(self, db, sample_project, sample_user):
        service = ProjectService()
        assert service.can_access_project(sample_project.id, sample_user.id) is True

    def test_non_member_cannot_access(self, db, sample_project, second_user):
        service = ProjectService()
        assert service.can_access_project(sample_project.id, second_user.id) is False

    def test_can_modify_nonexistent_project(self, db, sample_user):
        service = ProjectService()
        assert service.can_modify_project(99999, sample_user.id) is False


@pytest.mark.unit
class TestProjectServiceUpdate:
    """ProjectService.update_project"""

    def test_update_project_success(self, db, sample_project, sample_user):
        service = ProjectService()
        updated, error = service.update_project(
            sample_project.id, sample_user.id, name='Renamed'
        )
        assert error is None
        assert updated.name == 'Renamed'

    def test_update_project_not_found(self, db, sample_user):
        service = ProjectService()
        updated, error = service.update_project(99999, sample_user.id, name='X')
        assert updated is None
        assert 'not found' in error.lower()

    def test_update_project_unauthorized(self, db, sample_project, second_user):
        service = ProjectService()
        updated, error = service.update_project(
            sample_project.id, second_user.id, name='Hacked'
        )
        assert updated is None
        assert 'not authorized' in error.lower()


@pytest.mark.unit
class TestProjectServiceDelete:
    """ProjectService.delete_project"""

    def test_delete_project_success(self, db, sample_project, sample_user):
        service = ProjectService()
        success, error = service.delete_project(sample_project.id, sample_user.id)
        assert success is True
        assert error is None

    def test_delete_project_not_found(self, db, sample_user):
        service = ProjectService()
        success, error = service.delete_project(99999, sample_user.id)
        assert success is False
        assert 'not found' in error.lower()

    def test_delete_project_unauthorized(self, db, sample_project, second_user):
        service = ProjectService()
        success, error = service.delete_project(sample_project.id, second_user.id)
        assert success is False


@pytest.mark.unit
class TestProjectServiceMembers:
    """ProjectService member management"""

    def test_add_member_success(self, db, sample_project, sample_user, second_user):
        service = ProjectService()
        success, error = service.add_member(
            project_id=sample_project.id,
            user_id=sample_user.id,
            member_user_id=second_user.id,
            role='member'
        )
        assert success is True
        assert error is None

    def test_add_member_already_member(self, db, sample_project, sample_user):
        service = ProjectService()
        success, error = service.add_member(
            project_id=sample_project.id,
            user_id=sample_user.id,
            member_user_id=sample_user.id,
            role='member'
        )
        assert success is False
        assert 'already a member' in error.lower()

    def test_add_member_user_not_found(self, db, sample_project, sample_user):
        service = ProjectService()
        success, error = service.add_member(
            project_id=sample_project.id,
            user_id=sample_user.id,
            member_user_id=99999
        )
        assert success is False
        assert 'not found' in error.lower()

    def test_remove_owner_fails(self, db, sample_project, sample_user):
        service = ProjectService()
        success, error = service.remove_member(
            project_id=sample_project.id,
            user_id=sample_user.id,
            member_user_id=sample_user.id
        )
        assert success is False
        assert 'owner' in error.lower()

    def test_get_user_projects(self, db, sample_project, sample_user):
        service = ProjectService()
        projects = service.get_user_projects(sample_user.id)
        assert any(p.id == sample_project.id for p in projects)
