import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from optical_pos.db.database import Base
from optical_pos.services import inventory_service, product_service
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

# --- Helper to create a product ---
def create_test_product(db: Session, name: str, initial_stock: int) -> models.Product:
    return product_service.create_product(
        db=db,
        name=name,
        category="Test Category",
        price=10.0,
        stock_qty=initial_stock
    )

# --- Tests for Inventory Service ---

def test_record_inventory_movement_increase(db_session: Session):
    """
    Test recording a positive inventory movement (e.g., receiving stock).
    """
    product = create_test_product(db_session, "Product A", 10)

    movement = inventory_service.record_inventory_movement(
        db=db_session,
        product_id=product.id,
        qty_change=5,
        reason="stock_in"
    )

    assert movement is not None
    assert movement.qty_change == 5
    assert movement.reason == "stock_in"

    # Verify product stock is updated
    updated_product = product_service.get_product(db_session, product.id)
    assert updated_product.stock_qty == 15

def test_record_inventory_movement_decrease(db_session: Session):
    """
    Test recording a negative inventory movement (e.g., sale).
    """
    product = create_test_product(db_session, "Product B", 20)

    movement = inventory_service.record_inventory_movement(
        db=db_session,
        product_id=product.id,
        qty_change=-2,
        reason="sale"
    )

    assert movement is not None
    assert movement.qty_change == -2

    # Verify product stock is updated
    updated_product = product_service.get_product(db_session, product.id)
    assert updated_product.stock_qty == 18

def test_get_inventory_for_product(db_session: Session):
    """
    Test retrieving the inventory history for a product.
    """
    product = create_test_product(db_session, "Product C", 0)
    inventory_service.record_inventory_movement(db_session, product.id, 10, "initial_stock")
    inventory_service.record_inventory_movement(db_session, product.id, -3, "sale")

    history = inventory_service.get_inventory_for_product(db_session, product.id)

    assert len(history) == 2
    assert history[0].reason == "sale"
    assert history[0].qty_change == -3
    assert history[1].reason == "initial_stock"
    assert history[1].qty_change == 10

def test_get_low_stock_products(db_session: Session):
    """
    Test retrieving products with low stock.
    """
    create_test_product(db_session, "Low Stock Product", 5)
    create_test_product(db_session, "High Stock Product", 50)
    create_test_product(db_session, "Threshold Product", 10)

    low_stock_items = inventory_service.get_low_stock_products(db_session, threshold=10)

    assert len(low_stock_items) == 2
    product_names = {p.name for p in low_stock_items}
    assert "Low Stock Product" in product_names
    assert "Threshold Product" in product_names
    assert "High Stock Product" not in product_names
