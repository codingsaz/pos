from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QLabel,
    QLineEdit,
    QDateEdit,
    QComboBox,
    QDialogButtonBox,
)
from PySide6.QtCore import QDate
from typing import Optional, Dict, List
from optical_pos.db.models import Prescription, Customer

class PrescriptionForm(QDialog):
    def __init__(self, customers: List[Customer], prescription: Optional[Prescription] = None):
        super().__init__()

        self.is_edit_mode = prescription is not None
        self.customers = customers

        if self.is_edit_mode:
            self.setWindowTitle("Edit Prescription")
        else:
            self.setWindowTitle("Add Prescription")

        self.layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        # Form fields
        self.customer_combo = QComboBox()
        for customer in self.customers:
            self.customer_combo.addItem(customer.name, userData=customer.id)

        self.left_eye_input = QLineEdit()
        self.right_eye_input = QLineEdit()
        self.lens_type_input = QLineEdit()
        self.doctor_input = QLineEdit()
        self.date_input = QDateEdit(QDate.currentDate())
        self.date_input.setCalendarPopup(True)

        form_layout.addRow("Customer:", self.customer_combo)
        form_layout.addRow("Left Eye (OD):", self.left_eye_input)
        form_layout.addRow("Right Eye (OS):", self.right_eye_input)
        form_layout.addRow("Lens Type:", self.lens_type_input)
        form_layout.addRow("Doctor:", self.doctor_input)
        form_layout.addRow("Date:", self.date_input)

        self.layout.addLayout(form_layout)

        # Pre-fill data if in edit mode
        if self.is_edit_mode:
            customer_index = self.customer_combo.findData(prescription.customer_id)
            if customer_index >= 0:
                self.customer_combo.setCurrentIndex(customer_index)
            self.left_eye_input.setText(prescription.left_eye)
            self.right_eye_input.setText(prescription.right_eye)
            self.lens_type_input.setText(prescription.lens_type)
            self.doctor_input.setText(prescription.doctor)
            self.date_input.setDate(QDate(prescription.date))

        # Dialog buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box)

    def get_data(self) -> Dict:
        """
        Returns the data entered in the form as a dictionary.
        """
        return {
            "customer_id": self.customer_combo.currentData(),
            "left_eye": self.left_eye_input.text(),
            "right_eye": self.right_eye_input.text(),
            "lens_type": self.lens_type_input.text(),
            "doctor": self.doctor_input.text(),
            "date": self.date_input.date().toPython(),
        }
