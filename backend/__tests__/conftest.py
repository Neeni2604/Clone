import pytest
from sqlmodel import Session, SQLModel, StaticPool, create_engine
from starlette.testclient import TestClient
from backend.database.schema import *
from backend.dependencies import get_session
from backend import app

@pytest.fixture
def session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as s:
        yield s

@pytest.fixture
def client(session):
    def _get_session_override():
        return session
    
    app.dependency_overrides[get_session] = _get_session_override
    yield TestClient(app)
    app.dependency_overrides.clear()


