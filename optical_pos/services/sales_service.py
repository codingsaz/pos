from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from optical_pos.db import models
from optical_pos.services import inventory_service

def create_sale(db: Session, customer_id: int, items: List[Dict], payment_type: str, discount: float = 0, tax: float = 0) -> models.Sale:
    """
    Creates a new sale, its associated items, and updates inventory.
    'items' is a list of dicts, e.g., [{'product_id': 1, 'qty': 2}, ...]
    """

    # Start a transaction
    try:
        subtotal = 0
        sale_items_to_create = []

        for item in items:
            product = db.query(models.Product).filter(models.Product.id == item['product_id']).first()
            if not product or product.stock_qty < item['qty']:
                raise ValueError(f"Not enough stock for product ID {item['product_id']}")

            line_total = product.price * item['qty']
            subtotal += line_total

            sale_item = models.SaleItem(
                product_id=item['product_id'],
                qty=item['qty'],
                price=product.price
            )
            sale_items_to_create.append(sale_item)

            # Record inventory movement
            inventory_service.record_inventory_movement(
                db=db,
                product_id=item['product_id'],
                qty_change=-item['qty'],
                reason=f"Sale"
            )

        total = subtotal + tax - discount

        db_sale = models.Sale(
            customer_id=customer_id,
            total=total,
            discount=discount,
            tax=tax,
            payment_type=payment_type
        )

        db.add(db_sale)
        db.flush() # Flush to get the db_sale.id for the sale_items

        for sale_item in sale_items_to_create:
            sale_item.sale_id = db_sale.id
            db.add(sale_item)

        db.commit()
        db.refresh(db_sale)
        return db_sale

    except ValueError as e:
        db.rollback()
        raise e
    except Exception as e:
        db.rollback()
        raise e

def get_sale(db: Session, sale_id: int) -> Optional[models.Sale]:
    """
    Retrieves a single sale by its ID, including its items.
    """
    return db.query(models.Sale).filter(models.Sale.id == sale_id).first()

def list_sales(db: Session, skip: int = 0, limit: int = 100) -> List[models.Sale]:
    """
    Retrieves a list of sales with pagination.
    """
    return db.query(models.Sale).order_by(models.Sale.date.desc()).offset(skip).limit(limit).all()
