"""Unit tests for IssueService, CommentService and LabelService."""

import pytest
from src.services import IssueService, CommentService, LabelService


# ── IssueService ───────────────────────────────────────────────────────────

@pytest.mark.unit
class TestIssueServiceCreate:
    """IssueService.create_issue"""

    def test_create_issue_success(self, db, sample_project, sample_user):
        service = IssueService()
        issue, error = service.create_issue(
            project_id=sample_project.id,
            title='Test Bug',
            reporter_id=sample_user.id,
            description='Something broke',
            priority='high',
            status='open'
        )
        assert issue is not None
        assert error is None
        assert issue.title == 'Test Bug'
        assert issue.priority == 'high'

    def test_create_issue_project_not_found(self, db, sample_user):
        service = IssueService()
        issue, error = service.create_issue(
            project_id=99999,
            title='Ghost',
            reporter_id=sample_user.id
        )
        assert issue is None
        assert 'not found' in error.lower()

    def test_create_issue_non_member(self, db, sample_project, second_user):
        service = IssueService()
        issue, error = service.create_issue(
            project_id=sample_project.id,
            title='Sneaky',
            reporter_id=second_user.id
        )
        assert issue is None
        assert 'not a member' in error.lower()


@pytest.mark.unit
class TestIssueServiceAccess:
    """IssueService authorization helpers"""

    def test_reporter_can_modify(self, db, sample_issue, sample_user):
        service = IssueService()
        assert service.can_modify_issue(sample_issue.id, sample_user.id) is True

    def test_non_member_cannot_modify(self, db, sample_issue, second_user):
        service = IssueService()
        assert service.can_modify_issue(sample_issue.id, second_user.id) is False

    def test_reporter_can_delete(self, db, sample_issue, sample_user):
        service = IssueService()
        assert service.can_delete_issue(sample_issue.id, sample_user.id) is True

    def test_non_member_cannot_delete(self, db, sample_issue, second_user):
        service = IssueService()
        assert service.can_delete_issue(sample_issue.id, second_user.id) is False

    def test_member_can_access(self, db, sample_issue, sample_user):
        service = IssueService()
        assert service.can_access_issue(sample_issue.id, sample_user.id) is True

    def test_non_member_cannot_access(self, db, sample_issue, second_user):
        service = IssueService()
        assert service.can_access_issue(sample_issue.id, second_user.id) is False

    def test_access_nonexistent_issue(self, db, sample_user):
        service = IssueService()
        assert service.can_access_issue(99999, sample_user.id) is False


@pytest.mark.unit
class TestIssueServiceUpdate:
    """IssueService.update_issue"""

    def test_update_issue_success(self, db, sample_issue, sample_user):
        service = IssueService()
        updated, error = service.update_issue(
            sample_issue.id, sample_user.id, status='in_progress', title='Updated'
        )
        assert error is None
        assert updated.status == 'in_progress'

    def test_update_issue_not_found(self, db, sample_user):
        service = IssueService()
        updated, error = service.update_issue(99999, sample_user.id, title='X')
        assert updated is None
        assert 'not found' in error.lower()

    def test_update_issue_unauthorized(self, db, sample_issue, second_user):
        service = IssueService()
        updated, error = service.update_issue(
            sample_issue.id, second_user.id, title='Hacked'
        )
        assert updated is None
        assert 'not authorized' in error.lower()


@pytest.mark.unit
class TestIssueServiceDelete:
    """IssueService.delete_issue"""

    def test_delete_issue_not_found(self, db, sample_user):
        service = IssueService()
        success, error = service.delete_issue(99999, sample_user.id)
        assert success is False
        assert 'not found' in error.lower()

    def test_delete_issue_unauthorized(self, db, sample_issue, second_user):
        service = IssueService()
        success, error = service.delete_issue(sample_issue.id, second_user.id)
        assert success is False
        assert 'not authorized' in error.lower()


@pytest.mark.unit
class TestIssueServiceAssignment:
    """IssueService assignment operations"""

    def test_assign_user_not_member(self, db, sample_issue, sample_user, second_user):
        service = IssueService()
        success, error = service.assign_user(
            issue_id=sample_issue.id,
            user_id=sample_user.id,
            assignee_id=second_user.id
        )
        assert success is False
        assert 'not a member' in error.lower()

    def test_assign_issue_not_found(self, db, sample_user, second_user):
        service = IssueService()
        success, error = service.assign_user(
            issue_id=99999,
            user_id=sample_user.id,
            assignee_id=second_user.id
        )
        assert success is False
        assert 'not found' in error.lower()

    def test_unassign_issue_not_found(self, db, sample_user, second_user):
        service = IssueService()
        success, error = service.unassign_user(
            issue_id=99999,
            user_id=sample_user.id,
            assignee_id=second_user.id
        )
        assert success is False
        assert 'not found' in error.lower()


@pytest.mark.unit
class TestIssueServiceLabels:
    """IssueService label operations"""

    def test_add_label_issue_not_found(self, db, sample_user, sample_label):
        service = IssueService()
        success, error = service.add_label(99999, sample_user.id, sample_label.id)
        assert success is False
        assert 'not found' in error.lower()

    def test_add_label_not_found(self, db, sample_issue, sample_user):
        service = IssueService()
        success, error = service.add_label(sample_issue.id, sample_user.id, 99999)
        assert success is False
        assert 'not found' in error.lower()

    def test_add_label_unauthorized(self, db, sample_issue, second_user, sample_label):
        service = IssueService()
        success, error = service.add_label(
            sample_issue.id, second_user.id, sample_label.id
        )
        assert success is False
        assert 'not authorized' in error.lower()

    def test_remove_label_not_on_issue(self, db, sample_issue, sample_user, sample_label):
        service = IssueService()
        success, error = service.remove_label(
            sample_issue.id, sample_user.id, sample_label.id
        )
        assert success is False
        assert 'not on this issue' in error.lower()


# ── CommentService ─────────────────────────────────────────────────────────

@pytest.mark.unit
class TestCommentServiceCreate:
    """CommentService.create_comment"""

    def test_create_comment_success(self, db, sample_issue, sample_user):
        service = CommentService()
        comment, error = service.create_comment(
            issue_id=sample_issue.id,
            author_id=sample_user.id,
            content='Great issue!'
        )
        assert comment is not None
        assert error is None
        assert comment.content == 'Great issue!'

    def test_create_comment_issue_not_found(self, db, sample_user):
        service = CommentService()
        comment, error = service.create_comment(
            issue_id=99999,
            author_id=sample_user.id,
            content='Ghost'
        )
        assert comment is None
        assert 'not found' in error.lower()

    def test_create_comment_not_member(self, db, sample_issue, second_user):
        service = CommentService()
        comment, error = service.create_comment(
            issue_id=sample_issue.id,
            author_id=second_user.id,
            content='Sneaky'
        )
        assert comment is None
        assert 'not a member' in error.lower()


@pytest.mark.unit
class TestCommentServiceAccess:
    """CommentService authorization helpers"""

    def test_author_can_modify(self, db, sample_comment, sample_user):
        service = CommentService()
        assert service.can_modify_comment(sample_comment.id, sample_user.id) is True

    def test_non_author_cannot_modify(self, db, sample_comment, second_user):
        service = CommentService()
        assert service.can_modify_comment(sample_comment.id, second_user.id) is False

    def test_can_modify_nonexistent_comment(self, db, sample_user):
        service = CommentService()
        assert service.can_modify_comment(99999, sample_user.id) is False

    def test_member_can_access(self, db, sample_comment, sample_user):
        service = CommentService()
        assert service.can_access_comment(sample_comment.id, sample_user.id) is True

    def test_non_member_cannot_access(self, db, sample_comment, second_user):
        service = CommentService()
        assert service.can_access_comment(sample_comment.id, second_user.id) is False


@pytest.mark.unit
class TestCommentServiceUpdate:
    """CommentService.update_comment"""

    def test_update_comment_success(self, db, sample_comment, sample_user):
        service = CommentService()
        updated, error = service.update_comment(
            sample_comment.id, sample_user.id, 'New content'
        )
        assert error is None
        assert updated.content == 'New content'

    def test_update_comment_not_found(self, db, sample_user):
        service = CommentService()
        updated, error = service.update_comment(99999, sample_user.id, 'X')
        assert updated is None
        assert 'not found' in error.lower()

    def test_update_comment_unauthorized(self, db, sample_comment, second_user):
        service = CommentService()
        updated, error = service.update_comment(
            sample_comment.id, second_user.id, 'Hacked'
        )
        assert updated is None
        assert 'not authorized' in error.lower()


@pytest.mark.unit
class TestCommentServiceDelete:
    """CommentService.delete_comment"""

    def test_delete_comment_not_found(self, db, sample_user):
        service = CommentService()
        success, error = service.delete_comment(99999, sample_user.id)
        assert success is False
        assert 'not found' in error.lower()

    def test_delete_comment_unauthorized(self, db, sample_comment, second_user):
        service = CommentService()
        success, error = service.delete_comment(sample_comment.id, second_user.id)
        assert success is False
        assert 'not authorized' in error.lower()


# ── LabelService ───────────────────────────────────────────────────────────

@pytest.mark.unit
class TestLabelServiceCreate:
    """LabelService.create_label"""

    def test_create_label_success(self, db, admin_user):
        service = LabelService()
        label, error = service.create_label(
            name='wontfix',
            user_id=admin_user.id,
            color='#CCCCCC'
        )
        assert label is not None
        assert error is None
        assert label.name == 'wontfix'

    def test_create_label_non_admin_rejected(self, db, sample_user):
        service = LabelService()
        label, error = service.create_label(
            name='blocked',
            user_id=sample_user.id
        )
        assert label is None
        assert 'admin' in error.lower()

    def test_create_label_duplicate_name(self, db, admin_user, sample_label):
        service = LabelService()
        label, error = service.create_label(
            name='bug',  # already exists as sample_label
            user_id=admin_user.id
        )
        assert label is None
        assert 'already exists' in error.lower()


@pytest.mark.unit
class TestLabelServiceCRUD:
    """LabelService get/update/delete"""

    def test_get_label_success(self, db, sample_label):
        service = LabelService()
        label = service.get_label(sample_label.id)
        assert label is not None
        assert label.id == sample_label.id

    def test_get_label_not_found(self, db):
        service = LabelService()
        label = service.get_label(99999)
        assert label is None

    def test_get_all_labels(self, db, sample_label):
        service = LabelService()
        labels = service.get_all_labels()
        assert any(l.id == sample_label.id for l in labels)

    def test_update_label_success(self, db, admin_user, sample_label):
        service = LabelService()
        updated, error = service.update_label(
            sample_label.id, admin_user.id, color='#0000FF'
        )
        assert error is None
        assert updated.color == '#0000FF'

    def test_update_label_non_admin(self, db, sample_user, sample_label):
        service = LabelService()
        updated, error = service.update_label(
            sample_label.id, sample_user.id, name='hacked'
        )
        assert updated is None
        assert 'admin' in error.lower()

    def test_update_label_not_found(self, db, admin_user):
        service = LabelService()
        updated, error = service.update_label(99999, admin_user.id, name='ghost')
        assert updated is None
        assert 'not found' in error.lower()

    def test_delete_label_non_admin(self, db, sample_user, sample_label):
        service = LabelService()
        success, error = service.delete_label(sample_label.id, sample_user.id)
        assert success is False
        assert 'admin' in error.lower()

    def test_delete_label_not_found(self, db, admin_user):
        service = LabelService()
        success, error = service.delete_label(99999, admin_user.id)
        assert success is False
        assert 'not found' in error.lower()
