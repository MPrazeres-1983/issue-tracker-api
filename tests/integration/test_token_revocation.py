"""Regression tests: existing JWTs must honor current account status and role."""
import pytest


@pytest.mark.integration
def test_disabled_user_cannot_use_existing_token(client, db, auth_headers, sample_user):
    sample_user.is_active = False
    db.session.commit()

    assert client.get('/api/v1/auth/me', headers=auth_headers).status_code == 401
    assert client.get('/api/v1/projects', headers=auth_headers).status_code == 401


@pytest.mark.integration
def test_demoted_admin_token_loses_label_write_access(client, db, admin_headers, admin_user):
    admin_user.role = 'developer'
    db.session.commit()

    response = client.post('/api/v1/labels', headers=admin_headers, json={
        'name': 'unexpected-admin-label', 'color': '#abcdef',
    })
    assert response.status_code == 403
