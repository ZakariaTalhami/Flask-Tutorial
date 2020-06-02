import pytest
from flaskr.db import get_db
from flask import session, g
from werkzeug.security import check_password_hash

import flaskr.auth as AUTH

MOCK_USERNAME = "john"
MOCK_PASSWORD = "JohnDew"


def test_register(client, app):
    assert client.get('/auth/register').status_code == 200
    response = client.post(
        '/auth/register',
        data={
            'username': MOCK_USERNAME,
            'password': MOCK_PASSWORD,
        }
    )
    assert response.status_code == 302
    assert 'http://localhost/auth/login' == response.headers['location']

    with app.app_context():
        user_record = get_db().execute(
            'SELECT * FROM user WHERE username = ?', (MOCK_USERNAME,)
        ).fetchone()

        assert user_record is not None
        assert check_password_hash(user_record['password'], MOCK_PASSWORD)
    pass


@pytest.mark.parametrize(
    ('username', 'password', 'message'), (
            ('', '', AUTH.USERNAME_REQUIRED),
            (MOCK_USERNAME, '', AUTH.PASSWORD_REQUIRED),
            ('', MOCK_PASSWORD, AUTH.USERNAME_REQUIRED),
            ('test', 'test', AUTH.USER_EXISTS.format(username='test')),
    ))
def test_register_validation(client, username, password, message):
    response = client.post(
        '/auth/register',
        data={
            'username': username,
            'password': password
        }
    )

    assert message in response.data.decode()


def test_login(client, auth):
    assert client.get('/auth/login').status_code == 200
    response = auth.login()
    assert response.status_code == 302
    assert 'http://localhost/' == response.headers['location']

    with client:
        client.get("/")
        assert session['user_id'] == 1
        assert g.user['username'] == 'test'


@pytest.mark.parametrize(
    ('username', 'password', 'message'), (
        ('', '', AUTH.INVALID_CREDENTIALS),
        ('test', MOCK_PASSWORD, AUTH.INVALID_CREDENTIALS),
        (MOCK_USERNAME, 'test', AUTH.INVALID_CREDENTIALS),
        (MOCK_USERNAME, MOCK_PASSWORD, AUTH.INVALID_CREDENTIALS),
    ))
def test_login_validation(auth, username, password, message):
    response = auth.login(username, password)
    assert message in response.data.decode()


def test_logout(client, auth):
    auth.login()

    with client:
        response = auth.logout()
        assert response.status_code == 302
        assert 'http://localhost/' == response.headers['location']

        assert 'user_id' not in session
