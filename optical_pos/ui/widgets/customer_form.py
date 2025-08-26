from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QDialogButtonBox,
)
from typing import Optional, Dict
from optical_pos.db.models import Customer

class CustomerForm(QDialog):
    def __init__(self, customer: Optional[Customer] = None):
        super().__init__()

        self.is_edit_mode = customer is not None

        if self.is_edit_mode:
            self.setWindowTitle("Edit Customer")
        else:
            self.setWindowTitle("Add Customer")

        self.layout = QVBoxLayout(self)

        # Form fields
        self.name_label = QLabel("Name:")
        self.name_input = QLineEdit()
        self.layout.addWidget(self.name_label)
        self.layout.addWidget(self.name_input)

        self.phone_label = QLabel("Phone:")
        self.phone_input = QLineEdit()
        self.layout.addWidget(self.phone_label)
        self.layout.addWidget(self.phone_input)

        self.email_label = QLabel("Email:")
        self.email_input = QLineEdit()
        self.layout.addWidget(self.email_label)
        self.layout.addWidget(self.email_input)

        # Pre-fill data if in edit mode
        if self.is_edit_mode:
            self.name_input.setText(customer.name)
            self.phone_input.setText(customer.phone)
            self.email_input.setText(customer.email)

        # Dialog buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box)

    def get_data(self) -> Dict[str, str]:
        """
        Returns the data entered in the form as a dictionary.
        """
        return {
            "name": self.name_input.text(),
            "phone": self.phone_input.text(),
            "email": self.email_input.text(),
        }
