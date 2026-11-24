import os
import sys
import tempfile

import pytest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from project import app, db

_fd, _db_path = tempfile.mkstemp(suffix=".sqlite")
os.close(_fd)

app.config["TESTING"] = True
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{_db_path}"


@pytest.fixture
def session():
    with app.app_context():
        db.drop_all()
        db.create_all()
        yield db.session
        db.session.remove()
        db.drop_all()
