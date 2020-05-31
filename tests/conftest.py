import pytest
import tempfile
from flaskr import create_app
from flaskr.db import init_db, get_db
import os


with open(os.path.join(os.path.dirname(__file__), 'data.sql'), 'rb') as f:
    _data_file = f.read().decode('utf8')


@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()
    app = create_app({
        'TESTING': True,
        'DATABASE': db_path
    })

    with app.app_context():
        init_db()
        get_db().executescript(_data_file)

    yield app

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()



class AuthActions:
    def __init__(self, client):
        self._client = client

    def login(self, username='test', password='test'):
        return self._client.post(
            "/auth/login",
            data={'username': username, 'password': password}
        )

    def logout(self):
        return self._clinet('/auth/logout')