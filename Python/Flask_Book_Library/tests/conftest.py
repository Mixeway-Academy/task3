import os
import sys

import pytest

# Make the project package importable regardless of the directory pytest is
# launched from (project root is the parent of this tests/ directory).
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from project import app, db  # noqa: E402


@pytest.fixture
def session():
    """Provide a clean database session for every test.

    Each test runs against freshly created tables and the data is dropped
    afterwards, so tests do not influence one another.
    """
    app.config["TESTING"] = True
    with app.app_context():
        db.drop_all()
        db.create_all()
        try:
            yield db.session
        finally:
            db.session.remove()
            db.drop_all()
