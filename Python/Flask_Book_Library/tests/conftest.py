import pytest
from project import app, db

@pytest.fixture
def session():
    with app.app_context():
        yield db.session
        db.session.rollback()
