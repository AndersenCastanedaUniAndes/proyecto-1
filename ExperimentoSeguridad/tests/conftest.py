"""
Pytest configuration and fixtures.
"""
import pytest
import tempfile
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.models.database import get_db, Base
from app.models.db_models import User


@pytest.fixture(scope="session")
def test_db():
    """Create a test database."""
    # Create temporary database
    db_fd, db_path = tempfile.mkstemp()
    os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"
    
    # Create engine and tables
    engine = create_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(bind=engine)
    
    yield db_path
    
    # Cleanup
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture(scope="function")
def db_session(test_db):
    """Create a database session for each test."""
    engine = create_engine(f"sqlite:///{test_db}")
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def client(test_db):
    """Create a test client."""
    # Override database dependency
    def override_get_db():
        engine = create_engine(f"sqlite:///{test_db}")
        TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        session = TestingSessionLocal()
        try:
            yield session
        finally:
            session.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def test_user_data():
    """Test user data."""
    return {
        "email": "test@example.com",
        "password": "testpassword123",
        "full_name": "Test User",
        "role": "user"
    }


@pytest.fixture
def test_admin_data():
    """Test admin data."""
    return {
        "email": "admin@example.com",
        "password": "adminpassword123",
        "full_name": "Admin User",
        "role": "admin"
    }


@pytest.fixture
def auth_headers(client, test_user_data):
    """Create authenticated headers for test user."""
    # Create user
    response = client.post("/users/", json=test_user_data)
    assert response.status_code == 201
    
    # Login
    login_data = {
        "username": test_user_data["email"],
        "password": test_user_data["password"]
    }
    response = client.post("/token", data=login_data)
    assert response.status_code == 200
    
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_headers(client, test_admin_data):
    """Create authenticated headers for admin user."""
    # Create admin
    response = client.post("/users/", json=test_admin_data)
    assert response.status_code == 201
    
    # Login
    login_data = {
        "username": test_admin_data["email"],
        "password": test_admin_data["password"]
    }
    response = client.post("/token", data=login_data)
    assert response.status_code == 200
    
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}