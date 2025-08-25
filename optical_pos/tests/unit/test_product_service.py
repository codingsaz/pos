import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from optical_pos.db.database import Base
from optical_pos.services import product_service
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

# --- Helper to create a supplier ---
def create_test_supplier(db: Session) -> models.Supplier:
    supplier = models.Supplier(name="Test Supplier", contact_info="supplier@test.com")
    db.add(supplier)
    db.commit()
    db.refresh(supplier)
    return supplier

# --- Tests for Product Service ---

def test_create_product(db_session: Session):
    supplier = create_test_supplier(db_session)
    product = product_service.create_product(
        db=db_session,
        name="Test Lens",
        category="Lenses",
        price=99.99,
        stock_qty=10,
        supplier_id=supplier.id
    )
    assert product is not None
    assert product.name == "Test Lens"
    assert product.price == 99.99
    assert product.supplier_id == supplier.id

    db_product = db_session.query(models.Product).filter(models.Product.id == product.id).first()
    assert db_product is not None
    assert db_product.name == "Test Lens"

def test_get_product(db_session: Session):
    product = product_service.create_product(db=db_session, name="Get Me Frame", category="Frames", price=150.0, stock_qty=5)

    retrieved_product = product_service.get_product(db=db_session, product_id=product.id)

    assert retrieved_product is not None
    assert retrieved_product.id == product.id
    assert retrieved_product.name == "Get Me Frame"

def test_list_products(db_session: Session):
    product_service.create_product(db=db_session, name="Product A", category="Cat A", price=10.0, stock_qty=1)
    product_service.create_product(db=db_session, name="Product B", category="Cat B", price=20.0, stock_qty=2)

    products = product_service.list_products(db=db_session)

    assert len(products) == 2
    assert products[0].name == "Product A"
    assert products[1].name == "Product B"

def test_update_product(db_session: Session):
    product = product_service.create_product(db=db_session, name="Original Frame", category="Frames", price=100.0, stock_qty=10)

    updated_product = product_service.update_product(
        db=db_session,
        product_id=product.id,
        name="Updated Frame",
        category="Luxury Frames",
        price=200.0,
        stock_qty=5
    )

    assert updated_product is not None
    assert updated_product.name == "Updated Frame"
    assert updated_product.price == 200.0
    assert updated_product.stock_qty == 5

    db_product = db_session.query(models.Product).filter(models.Product.id == product.id).first()
    assert db_product.name == "Updated Frame"

def test_delete_product(db_session: Session):
    product = product_service.create_product(db=db_session, name="To Be Deleted", category="Misc", price=5.0, stock_qty=1)

    deleted_product = product_service.delete_product(db=db_session, product_id=product.id)
    assert deleted_product is not None

    db_product = db_session.query(models.Product).filter(models.Product.id == product.id).first()
    assert db_product is None
