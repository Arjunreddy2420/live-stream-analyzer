"""Shared pytest fixtures.

Overrides DATABASE_URL to a temp SQLite file *before* the app (and therefore
its SQLAlchemy engine) is imported, so tests never touch a real Postgres
instance and don't require Docker.
"""

import os
import tempfile

import pytest

_db_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
os.environ["DATABASE_URL"] = f"sqlite:///{_db_file.name}"

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402


@pytest.fixture()
def client():
    """A TestClient with the app's lifespan (table creation, monitor startup/shutdown) run."""
    with TestClient(app) as test_client:
        yield test_client
