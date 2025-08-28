import os
import shutil
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTableView,
    QPushButton,
    QLabel,
    QLineEdit,
    QMessageBox,
)
from PySide6.QtCore import QAbstractTableModel, Qt, QModelIndex
from typing import List, Any
from optical_pos.db.models import Product
from optical_pos.services import product_service, supplier_service
from optical_pos.db.database import SessionLocal, PROJECT_ROOT
from optical_pos.ui.widgets.product_form import ProductForm

class ProductTableModel(QAbstractTableModel):
    def __init__(self, data: List[Product]):
        super().__init__()
        self._data = data
        self.headers = ["ID", "Name", "Category", "Price", "Stock Qty", "Supplier"]

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self._data)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self.headers)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        if role == Qt.DisplayRole:
            product = self._data[index.row()]
            supplier_name = product.supplier.name if product.supplier else "N/A"
            return [
                str(product.id),
                product.name,
                product.category,
                f"{product.price:.2f}",
                str(product.stock_qty),
                supplier_name
            ][index.column()]
        return None

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole) -> Any:
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.headers[section]
        return None

class ProductScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.main_layout = QVBoxLayout(self)
        self.images_dir = PROJECT_ROOT / "data" / "product_images"
        self.images_dir.mkdir(parents=True, exist_ok=True)

        title_label = QLabel("Product Management")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        self.main_layout.addWidget(title_label)

        toolbar_layout = QHBoxLayout()
        self.add_button = QPushButton("Add Product")
        self.add_button.clicked.connect(self.add_product)
        self.edit_button = QPushButton("Edit Product")
        self.edit_button.clicked.connect(self.edit_product)
        self.delete_button = QPushButton("Delete Product")
        self.delete_button.clicked.connect(self.delete_product)
        toolbar_layout.addWidget(self.add_button)
        toolbar_layout.addWidget(self.edit_button)
        toolbar_layout.addWidget(self.delete_button)
        toolbar_layout.addStretch()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search products...")
        self.main_layout.addLayout(toolbar_layout)

        self.table_view = QTableView()
        self.table_view.setSelectionBehavior(QTableView.SelectRows)
        self.table_view.setSelectionMode(QTableView.SingleSelection)
        self.main_layout.addWidget(self.table_view)

        self.refresh_products()

    def refresh_products(self):
        db_session = SessionLocal()
        try:
            products = product_service.list_products(db_session)
            print(f"DEBUG: Service returned products: {products}") # DEBUG
            self.table_model = ProductTableModel(products)
            self.table_view.setModel(self.table_model)
        finally:
            db_session.close()
        print(f"Refreshed product list. Found {len(products)} products.")

    def _handle_image_upload(self, new_image_path: str) -> Any:
        if not new_image_path:
            return None
        try:
            image_filename = os.path.basename(new_image_path)
            dest_path = self.images_dir / image_filename
            shutil.copy(new_image_path, dest_path)
            return str(Path("product_images") / image_filename)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not save image: {e}")
            return None

    def add_product(self):
        db_session = SessionLocal()
        try:
            suppliers = supplier_service.list_suppliers(db_session)
            form = ProductForm(suppliers=suppliers)
            if form.exec():
                data = form.get_data()
                new_image_path = self._handle_image_upload(data.pop("image_path"))
                data["image_path"] = new_image_path

                product_service.create_product(db_session, **data)
                self.refresh_products()
                QMessageBox.information(self, "Success", "Product added successfully.")
        finally:
            db_session.close()

    def edit_product(self):
        selected_indexes = self.table_view.selectedIndexes()
        if not selected_indexes:
            QMessageBox.warning(self, "No Selection", "Please select a product to edit.")
            return

        row = selected_indexes[0].row()
        product_id = self.table_model.data(self.table_model.index(row, 0))

        db_session = SessionLocal()
        try:
            product = product_service.get_product(db_session, int(product_id))
            if not product:
                QMessageBox.critical(self, "Error", "Product not found.")
                return

            suppliers = supplier_service.list_suppliers(db_session)
            form = ProductForm(suppliers=suppliers, product=product)

            if form.exec():
                data = form.get_data()
                new_image_path = self._handle_image_upload(data.pop("image_path"))
                data["image_path"] = new_image_path if new_image_path else product.image_path

                product_service.update_product(db_session, product.id, **data)
                self.refresh_products()
                QMessageBox.information(self, "Success", "Product updated successfully.")
        finally:
            db_session.close()

    def delete_product(self):
        selected_indexes = self.table_view.selectedIndexes()
        if not selected_indexes:
            QMessageBox.warning(self, "No Selection", "Please select a product to delete.")
            return

        row = selected_indexes[0].row()
        product_id = self.table_model.data(self.table_model.index(row, 0))
        product_name = self.table_model.data(self.table_model.index(row, 1))

        reply = QMessageBox.question(
            self, "Confirm Delete", f"Are you sure you want to delete '{product_name}'?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            db_session = SessionLocal()
            try:
                product_service.delete_product(db_session, int(product_id))
                self.refresh_products()
                QMessageBox.information(self, "Success", "Product deleted successfully.")
            finally:
                db_session.close()
