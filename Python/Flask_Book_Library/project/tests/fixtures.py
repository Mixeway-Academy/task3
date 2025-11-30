import pytest
from project import app as flask_app
from project import db as flask_db

@pytest.fixture(scope='module')
def app():
    """Przygotowuje aplikację w trybie testowym."""
    flask_app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
    })

    with flask_app.app_context():
        yield flask_app

@pytest.fixture(scope='function')
def session(app):
    """Tworzy nową bazę danych dla każdego testu."""
    flask_db.create_all()
    yield flask_db.session
    flask_db.session.remove()
    flask_db.drop_all()
