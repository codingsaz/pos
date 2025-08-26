from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QLabel,
    QLineEdit,
    QComboBox,
    QPushButton,
    QDialogButtonBox,
    QFileDialog,
)
from typing import Optional, Dict, List
from optical_pos.db.models import Product, Supplier

class ProductForm(QDialog):
    def __init__(self, suppliers: List[Supplier], product: Optional[Product] = None):
        super().__init__()

        self.is_edit_mode = product is not None
        self.suppliers = suppliers
        self.new_image_path = None

        if self.is_edit_mode:
            self.setWindowTitle("Edit Product")
        else:
            self.setWindowTitle("Add Product")

        self.layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        # Form fields
        self.name_input = QLineEdit()
        self.category_input = QLineEdit()
        self.price_input = QLineEdit()
        self.stock_qty_input = QLineEdit()

        self.supplier_combo = QComboBox()
        for supplier in self.suppliers:
            self.supplier_combo.addItem(supplier.name, userData=supplier.id)

        self.image_button = QPushButton("Select Image")
        self.image_button.clicked.connect(self.select_image)
        self.image_label = QLabel("No image selected.")

        form_layout.addRow("Name:", self.name_input)
        form_layout.addRow("Category:", self.category_input)
        form_layout.addRow("Price:", self.price_input)
        form_layout.addRow("Stock Qty:", self.stock_qty_input)
        form_layout.addRow("Supplier:", self.supplier_combo)
        form_layout.addRow(self.image_button, self.image_label)

        self.layout.addLayout(form_layout)

        # Pre-fill data if in edit mode
        if self.is_edit_mode:
            self.name_input.setText(product.name)
            self.category_input.setText(product.category)
            self.price_input.setText(str(product.price))
            self.stock_qty_input.setText(str(product.stock_qty))
            if product.supplier_id:
                index = self.supplier_combo.findData(product.supplier_id)
                if index >= 0:
                    self.supplier_combo.setCurrentIndex(index)
            if product.image_path:
                self.image_label.setText(product.image_path)


        # Dialog buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box)

    def select_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Product Image", "", "Image Files (*.png *.jpg *.jpeg)")
        if file_path:
            self.new_image_path = file_path
            self.image_label.setText(file_path)

    def get_data(self) -> Dict:
        """
        Returns the data entered in the form as a dictionary.
        """
        return {
            "name": self.name_input.text(),
            "category": self.category_input.text(),
            "price": float(self.price_input.text()),
            "stock_qty": int(self.stock_qty_input.text()),
            "supplier_id": self.supplier_combo.currentData(),
            "image_path": self.new_image_path, # This will be the new path, or None
        }
