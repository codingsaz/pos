from sqlalchemy.orm import Session
from typing import List, Optional
from optical_pos.db import models

def create_customer(db: Session, name: str, phone: str, email: str) -> models.Customer:
    """
    Creates a new customer in the database.
    """
    db_customer = models.Customer(name=name, phone=phone, email=email)
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer

def get_customer(db: Session, customer_id: int) -> Optional[models.Customer]:
    """
    Retrieves a single customer by their ID.
    """
    return db.query(models.Customer).filter(models.Customer.id == customer_id).first()

def list_customers(db: Session, skip: int = 0, limit: int = 100) -> List[models.Customer]:
    """
    Retrieves a list of customers with pagination.
    """
    return db.query(models.Customer).offset(skip).limit(limit).all()

def update_customer(db: Session, customer_id: int, name: str, phone: str, email: str) -> Optional[models.Customer]:
    """
    Updates a customer's details.
    """
    db_customer = get_customer(db, customer_id)
    if db_customer:
        db_customer.name = name
        db_customer.phone = phone
        db_customer.email = email
        db.commit()
        db.refresh(db_customer)
    return db_customer

def delete_customer(db: Session, customer_id: int) -> Optional[models.Customer]:
    """
    Deletes a customer from the database.
    """
    db_customer = get_customer(db, customer_id)
    if db_customer:
        db.delete(db_customer)
        db.commit()
    return db_customer
