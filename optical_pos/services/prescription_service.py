from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from datetime import date
from optical_pos.db import models

def create_prescription(db: Session, customer_id: int, data: Dict) -> models.Prescription:
    """
    Creates a new prescription for a customer.
    'data' is a dictionary with prescription details.
    """
    db_prescription = models.Prescription(
        customer_id=customer_id,
        left_eye=data.get("left_eye"),
        right_eye=data.get("right_eye"),
        lens_type=data.get("lens_type"),
        doctor=data.get("doctor"),
        date=data.get("date", date.today())
    )
    db.add(db_prescription)
    db.commit()
    db.refresh(db_prescription)
    return db_prescription

def get_prescription(db: Session, prescription_id: int) -> Optional[models.Prescription]:
    """
    Retrieves a single prescription by its ID.
    """
    return db.query(models.Prescription).filter(models.Prescription.id == prescription_id).first()

def list_prescriptions_for_customer(db: Session, customer_id: int) -> List[models.Prescription]:
    """
    Retrieves all prescriptions for a specific customer.
    """
    return db.query(models.Prescription).filter(models.Prescription.customer_id == customer_id).order_by(models.Prescription.date.desc()).all()

def update_prescription(db: Session, prescription_id: int, data: Dict) -> Optional[models.Prescription]:
    """
    Updates a prescription's details.
    """
    db_prescription = get_prescription(db, prescription_id)
    if db_prescription:
        for key, value in data.items():
            setattr(db_prescription, key, value)
        db.commit()
        db.refresh(db_prescription)
    return db_prescription

def delete_prescription(db: Session, prescription_id: int) -> Optional[models.Prescription]:
    """
    Deletes a prescription.
    """
    db_prescription = get_prescription(db, prescription_id)
    if db_prescription:
        db.delete(db_prescription)
        db.commit()
    return db_prescription
