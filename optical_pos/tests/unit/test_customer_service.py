import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from optical_pos.db.database import Base
from optical_pos.services import customer_service
from optical_pos.db import models

# --- Test Database Setup ---
# Use an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- Pytest Fixture for DB Session ---
@pytest.fixture(scope="function")
def db_session() -> Session:
    """
    Pytest fixture to create a new database session for each test function.
    It creates all tables, yields a session, and then drops all tables after the test.
    """
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

# --- Tests for Customer Service ---

def test_create_customer(db_session: Session):
    """
    Test creating a new customer.
    """
    customer_name = "Test Customer"
    customer_phone = "1234567890"
    customer_email = "test@example.com"

    customer = customer_service.create_customer(
        db=db_session,
        name=customer_name,
        phone=customer_phone,
        email=customer_email
    )

    assert customer is not None
    assert customer.name == customer_name
    assert customer.email == customer_email
    assert customer.id is not None

    # Verify it's in the DB
    db_customer = db_session.query(models.Customer).filter(models.Customer.id == customer.id).first()
    assert db_customer is not None
    assert db_customer.name == customer_name

def test_get_customer(db_session: Session):
    """
    Test retrieving a customer by ID.
    """
    customer = customer_service.create_customer(db=db_session, name="Get Me", phone="9876543210", email="getme@example.com")

    retrieved_customer = customer_service.get_customer(db=db_session, customer_id=customer.id)

    assert retrieved_customer is not None
    assert retrieved_customer.id == customer.id
    assert retrieved_customer.name == "Get Me"

def test_list_customers(db_session: Session):
    """
    Test listing all customers.
    """
    customer_service.create_customer(db=db_session, name="Customer A", phone="111", email="a@a.com")
    customer_service.create_customer(db=db_session, name="Customer B", phone="222", email="b@b.com")

    customers = customer_service.list_customers(db=db_session)

    assert len(customers) == 2
    assert customers[0].name == "Customer A"
    assert customers[1].name == "Customer B"

def test_update_customer(db_session: Session):
    """
    Test updating a customer's details.
    """
    customer = customer_service.create_customer(db=db_session, name="Original Name", phone="000", email="original@o.com")

    updated_customer = customer_service.update_customer(
        db=db_session,
        customer_id=customer.id,
        name="Updated Name",
        phone="111",
        email="updated@u.com"
    )

    assert updated_customer is not None
    assert updated_customer.name == "Updated Name"
    assert updated_customer.email == "updated@u.com"

    # Verify the change in the DB
    db_customer = db_session.query(models.Customer).filter(models.Customer.id == customer.id).first()
    assert db_customer.name == "Updated Name"

def test_delete_customer(db_session: Session):
    """
    Test deleting a customer.
    """
    customer = customer_service.create_customer(db=db_session, name="To Be Deleted", phone="333", email="delete@d.com")

    # Delete the customer
    deleted_customer = customer_service.delete_customer(db=db_session, customer_id=customer.id)
    assert deleted_customer is not None

    # Verify it's gone from the DB
    db_customer = db_session.query(models.Customer).filter(models.Customer.id == customer.id).first()
    assert db_customer is None
