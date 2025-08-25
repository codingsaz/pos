from sqlalchemy.orm import Session
from typing import List, Optional
from optical_pos.db import models
from datetime import datetime, timezone

def record_inventory_movement(db: Session, product_id: int, qty_change: int, reason: str) -> Optional[models.InventoryMovement]:
    """
    Records an inventory movement and updates the product's stock quantity.
    - A positive qty_change increases stock (e.g., purchase, return).
    - A negative qty_change decreases stock (e.g., sale, damage).
    """
    # First, get the product
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        return None

    # Update the product's stock quantity
    product.stock_qty += qty_change

    # Create the inventory movement record
    db_movement = models.InventoryMovement(
        product_id=product_id,
        qty_change=qty_change,
        reason=reason,
        date=datetime.now(timezone.utc)
    )

    db.add(db_movement)
    db.add(product) # Add the updated product to the session
    db.commit()
    db.refresh(db_movement)

    return db_movement

def get_inventory_for_product(db: Session, product_id: int) -> List[models.InventoryMovement]:
    """
    Retrieves all inventory movements for a specific product.
    """
    return db.query(models.InventoryMovement).filter(models.InventoryMovement.product_id == product_id).order_by(models.InventoryMovement.date.desc()).all()

def get_low_stock_products(db: Session, threshold: int = 10) -> List[models.Product]:
    """
    Retrieves a list of products where the stock quantity is at or below a given threshold.
    """
    return db.query(models.Product).filter(models.Product.stock_qty <= threshold).all()
