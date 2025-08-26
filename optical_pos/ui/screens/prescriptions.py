from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTableView,
    QPushButton,
    QLabel,
    QMessageBox,
    QFileDialog,
)
from PySide6.QtCore import QAbstractTableModel, Qt, QModelIndex
from typing import List, Any
from optical_pos.db.models import Prescription
from optical_pos.services import prescription_service, customer_service
from optical_pos.db.database import SessionLocal
from optical_pos.ui.widgets.prescription_form import PrescriptionForm
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch

class PrescriptionTableModel(QAbstractTableModel):
    def __init__(self, data: List[Prescription]):
        super().__init__()
        self._data = data
        self.headers = ["ID", "Customer", "Doctor", "Date", "Lens Type"]

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self._data)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self.headers)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        if role == Qt.DisplayRole:
            prescription = self._data[index.row()]
            customer_name = prescription.customer.name if prescription.customer else "N/A"
            return [
                str(prescription.id),
                customer_name,
                prescription.doctor,
                prescription.date.strftime("%Y-%m-%d"),
                prescription.lens_type,
            ][index.column()]
        return None

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole) -> Any:
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.headers[section]
        return None

class PrescriptionScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.main_layout = QVBoxLayout(self)

        title_label = QLabel("Prescription Management")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        self.main_layout.addWidget(title_label)

        # In a real app, you'd have a customer selector here.
        # For now, we list all prescriptions.

        toolbar_layout = QHBoxLayout()
        self.add_button = QPushButton("Add Prescription")
        self.add_button.clicked.connect(self.add_prescription)
        self.export_button = QPushButton("Export to PDF")
        self.export_button.clicked.connect(self.export_pdf)
        toolbar_layout.addWidget(self.add_button)
        toolbar_layout.addWidget(self.export_button)
        toolbar_layout.addStretch()
        self.main_layout.addLayout(toolbar_layout)

        self.table_view = QTableView()
        self.table_view.setSelectionBehavior(QTableView.SelectRows)
        self.table_view.setSelectionMode(QTableView.SingleSelection)
        self.main_layout.addWidget(self.table_view)

        self.refresh_prescriptions()

    def refresh_prescriptions(self):
        db_session = SessionLocal()
        try:
            # This is inefficient for large numbers of prescriptions.
            # A better approach would be to fetch for a selected customer.
            prescriptions = db_session.query(Prescription).all()
            self.table_model = PrescriptionTableModel(prescriptions)
            self.table_view.setModel(self.table_model)
        finally:
            db_session.close()

    def add_prescription(self):
        db_session = SessionLocal()
        try:
            customers = customer_service.list_customers(db_session)
            if not customers:
                QMessageBox.warning(self, "No Customers", "Please add a customer before adding a prescription.")
                return

            form = PrescriptionForm(customers=customers)
            if form.exec():
                data = form.get_data()
                customer_id = data.pop("customer_id")
                prescription_service.create_prescription(db_session, customer_id, data)
                self.refresh_prescriptions()
                QMessageBox.information(self, "Success", "Prescription added successfully.")
        finally:
            db_session.close()

    def export_pdf(self):
        selected_indexes = self.table_view.selectedIndexes()
        if not selected_indexes:
            QMessageBox.warning(self, "No Selection", "Please select a prescription to export.")
            return

        row = selected_indexes[0].row()
        prescription_id = self.table_model.data(self.table_model.index(row, 0))

        db_session = SessionLocal()
        try:
            prescription = prescription_service.get_prescription(db_session, int(prescription_id))
            if not prescription:
                QMessageBox.critical(self, "Error", "Prescription not found.")
                return

            file_path, _ = QFileDialog.getSaveFileName(self, "Save Prescription PDF", f"prescription_{prescription.id}.pdf", "PDF Files (*.pdf)")
            if not file_path:
                return

            self._generate_pdf(file_path, prescription)
            QMessageBox.information(self, "Success", f"Successfully exported PDF to {file_path}")

        finally:
            db_session.close()

    def _generate_pdf(self, file_path: str, prescription: Prescription):
        c = canvas.Canvas(file_path, pagesize=letter)
        width, height = letter

        c.setFont("Helvetica-Bold", 16)
        c.drawString(1 * inch, height - 1 * inch, "Eye Prescription")

        c.setFont("Helvetica", 12)
        text_y = height - 1.5 * inch

        c.drawString(1 * inch, text_y, f"Customer: {prescription.customer.name}")
        c.drawString(1 * inch, text_y - 20, f"Doctor: {prescription.doctor}")
        c.drawString(1 * inch, text_y - 40, f"Date: {prescription.date.strftime('%Y-%m-%d')}")

        text_y -= 80
        c.setFont("Helvetica-Bold", 12)
        c.drawString(1 * inch, text_y, "Right Eye (OD):")
        c.drawString(4 * inch, text_y, "Left Eye (OS):")

        c.setFont("Helvetica", 12)
        c.drawString(1 * inch, text_y - 20, prescription.right_eye)
        c.drawString(4 * inch, text_y - 20, prescription.left_eye)

        text_y -= 60
        c.setFont("Helvetica-Bold", 12)
        c.drawString(1 * inch, text_y, "Lens Type:")
        c.setFont("Helvetica", 12)
        c.drawString(1 * inch, text_y - 20, prescription.lens_type)

        c.save()
