from sqlalchemy.orm import Session
from typing import List, Optional
from optical_pos.db import models

def create_product(db: Session, name: str, category: str, price: float, stock_qty: int, supplier_id: Optional[int] = None) -> models.Product:
    """
    Creates a new product in the database.
    """
    db_product = models.Product(
        name=name,
        category=category,
        price=price,
        stock_qty=stock_qty,
        supplier_id=supplier_id
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def get_product(db: Session, product_id: int) -> Optional[models.Product]:
    """
    Retrieves a single product by its ID.
    """
    return db.query(models.Product).filter(models.Product.id == product_id).first()

def list_products(db: Session, skip: int = 0, limit: int = 100) -> List[models.Product]:
    """
    Retrieves a list of products with pagination.
    """
    return db.query(models.Product).offset(skip).limit(limit).all()

def update_product(db: Session, product_id: int, name: str, category: str, price: float, stock_qty: int) -> Optional[models.Product]:
    """
    Updates a product's details.
    """
    db_product = get_product(db, product_id)
    if db_product:
        db_product.name = name
        db_product.category = category
        db_product.price = price
        db_product.stock_qty = stock_qty
        db.commit()
        db.refresh(db_product)
    return db_product

def delete_product(db: Session, product_id: int) -> Optional[models.Product]:
    """
    Deletes a product from the database.
    """
    db_product = get_product(db, product_id)
    if db_product:
        db.delete(db_product)
        db.commit()
    return db_product
