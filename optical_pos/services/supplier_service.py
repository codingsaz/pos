from sqlalchemy.orm import Session
from typing import List, Optional
from optical_pos.db import models

def create_supplier(db: Session, name: str, contact_info: str) -> models.Supplier:
    """
    Creates a new supplier.
    """
    db_supplier = models.Supplier(name=name, contact_info=contact_info)
    db.add(db_supplier)
    db.commit()
    db.refresh(db_supplier)
    return db_supplier

def get_supplier(db: Session, supplier_id: int) -> Optional[models.Supplier]:
    """
    Retrieves a single supplier by their ID.
    """
    return db.query(models.Supplier).filter(models.Supplier.id == supplier_id).first()

def list_suppliers(db: Session) -> List[models.Supplier]:
    """
    Retrieves a list of all suppliers.
    """
    return db.query(models.Supplier).order_by(models.Supplier.name).all()

def update_supplier(db: Session, supplier_id: int, name: str, contact_info: str) -> Optional[models.Supplier]:
    """
    Updates a supplier's details.
    """
    db_supplier = get_supplier(db, supplier_id)
    if db_supplier:
        db_supplier.name = name
        db_supplier.contact_info = contact_info
        db.commit()
        db.refresh(db_supplier)
    return db_supplier

def delete_supplier(db: Session, supplier_id: int) -> Optional[models.Supplier]:
    """
    Deletes a supplier.
    """
    db_supplier = get_supplier(db, supplier_id)
    if db_supplier:
        db.delete(db_supplier)
        db.commit()
    return db_supplier
