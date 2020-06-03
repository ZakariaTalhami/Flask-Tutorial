import pytest
from flaskr.db import get_db
import flaskr.blog as BLOG


@pytest.mark.parametrize(
    'path',
    '/1'
    '/'
)
def test_index_viewer(client, auth, path):
    response = client.get(path)
    assert response.status_code == 200
    assert b'Log In' in response.data

    auth.login()
    response = client.get('/')

    assert b'Log Out' in response.data
    assert b'test title' in response.data
    assert b'by test on 2018-01-01' in response.data
    assert b'test\nbody' in response.data
    assert b'href="/1/update"' in response.data


@pytest.mark.parametrize('path', (
    '/1/update',
    '/1/delete',
    '/create',
))
def test_login_required(client, path):
    response = client.post(path)
    assert response.status_code == 302
    assert response.headers['location'] == 'http://localhost/auth/login'


def test_author_required(app, client, auth):
    with app.app_context():
        db = get_db()
        db.execute('UPDATE post SET author_id = 2 WHERE id = 1')
        db.commit()

    auth.login()

    assert client.post('/1/update').status_code == 403
    assert client.post('/1/delete').status_code == 403

    assert b'href="/1/update"' not in client.get('/').data


@pytest.mark.parametrize(
    'path', (
       '/2/update',
       '/2/delete',
    ))
def test_exists_required(client, auth, path):
    auth.login()
    assert client.post(path).status_code == 404


def test_create(client, auth, app):
    auth.login()
    assert client.get('/create').status_code == 200

    client.post(
        '/create',
        data={
            'title': "created",
            'body': "Testing creation"
        }
    )

    with app.app_context():
        db = get_db()
        post_count = db.execute('SELECT COUNT(id) FROM post').fetchone()[0]
        assert post_count == 2


def test_update(client, auth, app):
    auth.login()
    assert client.get('/1/update').status_code == 200

    client.post(
        "/1/update",
        data={
            "title": "Updated",
            "body": "Testing update"
        }
    )

    with app.app_context():
        db = get_db()
        post = db.execute('SELECT * FROM post WHERE id = 1').fetchone()

        assert post['title'] == "Updated"
        assert post['body'] == "Testing update"


@pytest.mark.parametrize(
    ('path', 'title', 'body', 'message'), (
            ('/create', '', '', BLOG.TITLE_REQUIRED),
            ('/create', 'A Title', '', BLOG.BODY_REQUIRED),
            ('/1/update', '', '', BLOG.TITLE_REQUIRED),
            ('/1/update', 'A Title', '', BLOG.BODY_REQUIRED),
    )
)
def test_create_update_validation(client, auth, path, title, body, message):
    auth.login()
    response = client.post(
        path,
        data={
            'title': title,
            'body': body
        }
    )

    assert message in response.data.decode()


def test_delete(client, auth, app):
    auth.login()
    response = client.post('/1/delete')
    assert response.status_code == 302
    assert response.headers['location'] == 'http://localhost/'

    with app.app_context():
        db = get_db()
        post = db.execute('SELECT * FROM post WHERE id = 1').fetchone()
        assert post is None
