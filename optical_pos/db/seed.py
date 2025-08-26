import datetime
from sqlalchemy.orm import Session
from .database import SessionLocal, init_db
from .models import User, Customer, Supplier, Product, Prescription
from optical_pos.services.auth_service import get_password_hash

def seed_data():
    """
    Seeds the database with initial data if it's empty.
    """
    db: Session = SessionLocal()

    # Check if data already exists
    if db.query(User).first():
        print("Database already seeded.")
        db.close()
        return

    print("Seeding database with initial data...")

    # Create users
    admin_password_hash = get_password_hash("admin123")
    admin_user = User(username="admin", password_hash=admin_password_hash, role="Admin")
    db.add(admin_user)

    # Create a supplier
    main_supplier = Supplier(name="VisionWorks Supply", contact_info="123-456-7890")
    db.add(main_supplier)

    # Commit to get IDs for foreign keys
    db.commit()

    # Create products
    product1 = Product(name="Ray-Ban Aviator", category="Sunglasses", price=150.00, stock_qty=20, supplier_id=main_supplier.id)
    product2 = Product(name="Oakley Holbrook", category="Sunglasses", price=120.00, stock_qty=15, supplier_id=main_supplier.id)
    product3 = Product(name="Generic Reading Glasses", category="Lenses", price=25.00, stock_qty=50, supplier_id=main_supplier.id)
    db.add_all([product1, product2, product3])

    # Create customers
    customer1 = Customer(name="John Doe", phone="555-0101", email="john.doe@example.com")
    customer2 = Customer(name="Jane Smith", phone="555-0102", email="jane.smith@example.com")
    db.add_all([customer1, customer2])

    # Commit to get IDs for foreign keys
    db.commit()

    # Create prescriptions
    prescription1 = Prescription(
        customer_id=customer1.id,
        left_eye="SPH: -1.25, CYL: -0.50, AXIS: 180",
        right_eye="SPH: -1.50, CYL: -0.50, AXIS: 175",
        lens_type="Single Vision",
        doctor="Dr. Adams",
        date=datetime.date(2023, 5, 10)
    )
    db.add(prescription1)

    db.commit()
    db.close()
    print("Database seeding complete.")


if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    seed_data()
