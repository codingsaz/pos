import pandas as pd
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTableView,
    QPushButton,
    QLabel,
    QLineEdit,
    QMessageBox,
    QFileDialog,
)
from PySide6.QtCore import QAbstractTableModel, Qt, QModelIndex
from typing import List, Any
from optical_pos.db.models import Customer
from optical_pos.services import customer_service
from optical_pos.db.database import SessionLocal
from optical_pos.ui.widgets.customer_form import CustomerForm

class CustomerTableModel(QAbstractTableModel):
    """
    A table model for displaying customer data in a QTableView.
    """
    def __init__(self, data: List[Customer]):
        super().__init__()
        self._data = data
        self.headers = ["ID", "Name", "Phone", "Email"]

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self._data)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self.headers)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        if role == Qt.DisplayRole:
            customer = self._data[index.row()]
            return [str(customer.id), customer.name, customer.phone, customer.email][index.column()]
        return None

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole) -> Any:
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.headers[section]
        return None

class CustomerScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.main_layout = QVBoxLayout(self)

        title_label = QLabel("Customer Management")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        self.main_layout.addWidget(title_label)

        toolbar_layout = QHBoxLayout()
        self.add_button = QPushButton("Add Customer")
        self.add_button.clicked.connect(self.add_customer)
        self.edit_button = QPushButton("Edit Customer")
        self.edit_button.clicked.connect(self.edit_customer)
        self.delete_button = QPushButton("Delete Customer")
        self.delete_button.clicked.connect(self.delete_customer)

        self.import_button = QPushButton("Import CSV")
        self.import_button.clicked.connect(self.import_csv)
        self.export_button = QPushButton("Export CSV")
        self.export_button.clicked.connect(self.export_csv)
        self.history_button = QPushButton("View History")
        self.history_button.clicked.connect(self.view_history)

        toolbar_layout.addWidget(self.add_button)
        toolbar_layout.addWidget(self.edit_button)
        toolbar_layout.addWidget(self.delete_button)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.history_button)
        toolbar_layout.addWidget(self.import_button)
        toolbar_layout.addWidget(self.export_button)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search customers...")
        toolbar_layout.addWidget(self.search_input)
        self.main_layout.addLayout(toolbar_layout)

        self.table_view = QTableView()
        self.table_view.setSelectionBehavior(QTableView.SelectRows)
        self.table_view.setSelectionMode(QTableView.SingleSelection)
        self.main_layout.addWidget(self.table_view)

        self.refresh_customers()

    def refresh_customers(self):
        db_session = SessionLocal()
        try:
            customers = customer_service.list_customers(db_session)
            self.table_model = CustomerTableModel(customers)
            self.table_view.setModel(self.table_model)
        finally:
            db_session.close()
        print(f"Refreshed customer list. Found {len(customers)} customers.")

    def add_customer(self):
        form = CustomerForm()
        if form.exec():
            data = form.get_data()
            db_session = SessionLocal()
            try:
                customer_service.create_customer(db_session, **data)
                self.refresh_customers()
                QMessageBox.information(self, "Success", "Customer added successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not add customer: {e}")
            finally:
                db_session.close()

    def edit_customer(self):
        selected_indexes = self.table_view.selectedIndexes()
        if not selected_indexes:
            QMessageBox.warning(self, "No Selection", "Please select a customer to edit.")
            return

        row = selected_indexes[0].row()
        customer_id = self.table_model.data(self.table_model.index(row, 0))

        db_session = SessionLocal()
        try:
            customer = customer_service.get_customer(db_session, int(customer_id))
            if not customer:
                QMessageBox.critical(self, "Error", "Customer not found.")
                return

            form = CustomerForm(customer=customer)
            if form.exec():
                data = form.get_data()
                customer_service.update_customer(db_session, customer.id, **data)
                self.refresh_customers()
                QMessageBox.information(self, "Success", "Customer updated successfully.")
        finally:
            db_session.close()

    def delete_customer(self):
        selected_indexes = self.table_view.selectedIndexes()
        if not selected_indexes:
            QMessageBox.warning(self, "No Selection", "Please select a customer to delete.")
            return

        row = selected_indexes[0].row()
        customer_id = self.table_model.data(self.table_model.index(row, 0))
        customer_name = self.table_model.data(self.table_model.index(row, 1))

        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete customer '{customer_name}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            db_session = SessionLocal()
            try:
                customer_service.delete_customer(db_session, int(customer_id))
                self.refresh_customers()
                QMessageBox.information(self, "Success", "Customer deleted successfully.")
            finally:
                db_session.close()

    def export_csv(self):
        """Exports the customer list to a CSV file."""
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Customers", "", "CSV Files (*.csv)")
        if not file_path:
            return

        db_session = SessionLocal()
        try:
            customers = customer_service.list_customers(db_session)
            customer_data = [{"id": c.id, "name": c.name, "phone": c.phone, "email": c.email} for c in customers]
            df = pd.DataFrame(customer_data)
            df.to_csv(file_path, index=False)
            QMessageBox.information(self, "Success", f"Successfully exported {len(customers)} customers to {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not export customers: {e}")
        finally:
            db_session.close()

    def import_csv(self):
        """Imports customers from a CSV file."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Import Customers", "", "CSV Files (*.csv)")
        if not file_path:
            return

        try:
            df = pd.read_csv(file_path)
            # Ensure required columns are present
            if not all(col in df.columns for col in ["name", "phone", "email"]):
                raise ValueError("CSV must have 'name', 'phone', and 'email' columns.")

            db_session = SessionLocal()
            imported_count = 0
            try:
                for _, row in df.iterrows():
                    # Simple check to avoid duplicates on phone/email
                    existing = db_session.query(Customer).filter(
                        (Customer.phone == row['phone']) | (Customer.email == row['email'])
                    ).first()
                    if not existing:
                        customer_service.create_customer(
                            db_session,
                            name=row['name'],
                            phone=str(row['phone']),
                            email=row['email']
                        )
                        imported_count += 1
                self.refresh_customers()
                QMessageBox.information(self, "Success", f"Successfully imported {imported_count} new customers.")
            finally:
                db_session.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not import customers: {e}")

    def view_history(self):
        """
        Placeholder method to show a customer's history.
        For now, it just prints to the console.
        """
        selected_indexes = self.table_view.selectedIndexes()
        if not selected_indexes:
            QMessageBox.warning(self, "No Selection", "Please select a customer to view their history.")
            return

        row = selected_indexes[0].row()
        customer_id = self.table_model.data(self.table_model.index(row, 0))

        db_session = SessionLocal()
        try:
            customer = customer_service.get_customer(db_session, int(customer_id))
            if not customer:
                QMessageBox.critical(self, "Error", "Customer not found.")
                return

            history_message = f"--- History for {customer.name} ---\n\n"

            history_message += f"Prescriptions ({len(customer.prescriptions)}):\n"
            if customer.prescriptions:
                for p in customer.prescriptions:
                    history_message += f"  - Dr. {p.doctor} on {p.date}: Left({p.left_eye}), Right({p.right_eye})\n"
            else:
                history_message += "  - No prescriptions on file.\n"

            history_message += f"\nSales ({len(customer.sales)}):\n"
            if customer.sales:
                for s in customer.sales:
                    history_message += f"  - Sale ID {s.id} on {s.date.strftime('%Y-%m-%d')}: Total ${s.total:.2f}\n"
            else:
                history_message += "  - No sales on file.\n"

            QMessageBox.information(self, f"History for {customer.name}", history_message)

        finally:
            db_session.close()
