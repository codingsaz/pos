import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from optical_pos.db.database import Base
from optical_pos.services import sales_service, customer_service, product_service
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

# --- Helper functions ---
def create_test_customer(db: Session):
    return customer_service.create_customer(db, name="Test Customer", phone="111", email="cust@test.com")

def create_test_products(db: Session):
    p1 = product_service.create_product(db, name="Product A", category="Cat A", price=10.0, stock_qty=20)
    p2 = product_service.create_product(db, name="Product B", category="Cat B", price=25.0, stock_qty=15)
    return p1, p2

# --- Tests for Sales Service ---

def test_create_sale_success(db_session: Session):
    """
    Test creating a successful sale and verifying all related data changes.
    """
    customer = create_test_customer(db_session)
    p1, p2 = create_test_products(db_session)

    sale_items = [
        {'product_id': p1.id, 'qty': 2},  # 2 * 10.0 = 20.0
        {'product_id': p2.id, 'qty': 1},  # 1 * 25.0 = 25.0
    ]

    sale = sales_service.create_sale(
        db=db_session,
        customer_id=customer.id,
        items=sale_items,
        payment_type="Cash"
    )

    assert sale is not None
    assert sale.customer_id == customer.id
    assert sale.total == 45.0  # subtotal
    assert len(sale.sale_items) == 2

    # Verify stock levels
    db_p1 = product_service.get_product(db_session, p1.id)
    db_p2 = product_service.get_product(db_session, p2.id)
    assert db_p1.stock_qty == 18  # 20 - 2
    assert db_p2.stock_qty == 14  # 15 - 1

def test_create_sale_insufficient_stock(db_session: Session):
    """
    Test that a sale fails if there is not enough stock for a product.
    """
    customer = create_test_customer(db_session)
    p1, _ = create_test_products(db_session) # p1 has 20 in stock

    sale_items = [{'product_id': p1.id, 'qty': 25}] # Try to sell 25

    with pytest.raises(ValueError, match="Not enough stock"):
        sales_service.create_sale(
            db=db_session,
            customer_id=customer.id,
            items=sale_items,
            payment_type="Cash"
        )

    # Verify no sale was created
    sales = sales_service.list_sales(db_session)
    assert len(sales) == 0

    # Verify stock was not changed
    db_p1 = product_service.get_product(db_session, p1.id)
    assert db_p1.stock_qty == 20

def test_get_and_list_sales(db_session: Session):
    """
    Test retrieving one and multiple sales.
    """
    customer = create_test_customer(db_session)
    p1, _ = create_test_products(db_session)

    sale1 = sales_service.create_sale(db_session, customer.id, [{'product_id': p1.id, 'qty': 1}], "Card")
    sale2 = sales_service.create_sale(db_session, customer.id, [{'product_id': p1.id, 'qty': 2}], "Cash")

    # Test list
    all_sales = sales_service.list_sales(db_session)
    assert len(all_sales) == 2

    # Test get
    retrieved_sale = sales_service.get_sale(db_session, sale1.id)
    assert retrieved_sale is not None
    assert retrieved_sale.id == sale1.id
    assert retrieved_sale.payment_type == "Card"
    assert len(retrieved_sale.sale_items) == 1
    assert retrieved_sale.sale_items[0].qty == 1
