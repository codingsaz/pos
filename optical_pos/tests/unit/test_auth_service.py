import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from optical_pos.db.database import Base
from optical_pos.services import auth_service
from optical_pos.db import models

# --- Test Database Setup ---
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- Pytest Fixture for DB Session ---
@pytest.fixture(scope="function")
def db_session() -> Session:
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

# --- Tests for Auth Service ---

def test_create_user(db_session: Session):
    """
    Test creating a new user and that the password is hashed.
    """
    username = "testuser"
    password = "password123"
    role = "Admin"

    user = auth_service.create_user(
        db=db_session,
        username=username,
        password=password,
        role=role
    )

    assert user is not None
    assert user.username == username
    assert user.role == role
    assert user.password_hash != password  # Make sure it's not plain text
    assert auth_service.verify_password(password, user.password_hash)

def test_authenticate_user_success(db_session: Session):
    """
    Test successful user authentication.
    """
    username = "authuser"
    password = "authpassword"
    auth_service.create_user(db=db_session, username=username, password=password, role="Cashier")

    authenticated_user = auth_service.authenticate_user(
        db=db_session,
        username=username,
        password=password
    )

    assert authenticated_user is not None
    assert authenticated_user.username == username

def test_authenticate_user_failure_wrong_password(db_session: Session):
    """
    Test failed authentication due to a wrong password.
    """
    username = "wrongpassuser"
    password = "correctpassword"
    auth_service.create_user(db=db_session, username=username, password=password, role="Cashier")

    authenticated_user = auth_service.authenticate_user(
        db=db_session,
        username=username,
        password="wrongpassword"
    )

    assert authenticated_user is None

def test_authenticate_user_failure_nonexistent_user(db_session: Session):
    """
    Test failed authentication for a user that does not exist.
    """
    authenticated_user = auth_service.authenticate_user(
        db=db_session,
        username="nouser",
        password="anypassword"
    )

    assert authenticated_user is None

def test_password_verification(db_session: Session):
    """
    Test the verify_password helper function directly.
    """
    password = "mypassword"
    hashed_password = auth_service.get_password_hash(password)

    assert auth_service.verify_password(password, hashed_password) is True
    assert auth_service.verify_password("notmypassword", hashed_password) is False
