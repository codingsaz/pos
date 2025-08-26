from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTableView,
    QPushButton,
    QLabel,
    QLineEdit,
    QFormLayout,
    QHeaderView,
    QMessageBox,
    QFileDialog,
)
from PySide6.QtCore import QAbstractTableModel, Qt, QModelIndex
from typing import List, Any, Dict
from optical_pos.db.models import Product
from optical_pos.services import product_service, sales_service, customer_service
from optical_pos.db.database import SessionLocal
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch

class CartTableModel(QAbstractTableModel):
    def __init__(self):
        super().__init__()
        self._data: List[Dict] = []
        self.headers = ["Product", "Price", "Qty", "Total"]

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self._data)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self.headers)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        if role == Qt.DisplayRole:
            item = self._data[index.row()]
            column = index.column()
            if column == 0: return item['product'].name
            if column == 1: return f"{item['product'].price:.2f}"
            if column == 2: return str(item['qty'])
            if column == 3: return f"{(item['product'].price * item['qty']):.2f}"
        return None

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole) -> Any:
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.headers[section]
        return None

    def add_item(self, product, qty: int):
        for item in self._data:
            if item['product'].id == product.id:
                item['qty'] += qty
                self.layoutChanged.emit()
                return
        self._data.append({'product': product, 'qty': qty})
        self.layoutChanged.emit()

    def get_cart_total(self) -> float:
        return sum(item['product'].price * item['qty'] for item in self._data)

    def get_cart_items(self) -> List[Dict]:
        return [{'product_id': item['product'].id, 'qty': item['qty']} for item in self._data]

    def clear_cart(self):
        self.beginResetModel()
        self._data = []
        self.endResetModel()

class SalesScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.main_layout = QHBoxLayout(self)

        left_layout = QVBoxLayout()
        product_input_layout = QHBoxLayout()
        self.product_input = QLineEdit()
        self.product_input.setPlaceholderText("Enter Product ID/SKU...")
        self.add_to_cart_button = QPushButton("Add to Cart")
        self.add_to_cart_button.clicked.connect(self.add_product_to_cart)
        product_input_layout.addWidget(self.product_input)
        product_input_layout.addWidget(self.add_to_cart_button)
        left_layout.addLayout(product_input_layout)

        self.cart_table_view = QTableView()
        self.cart_model = CartTableModel()
        self.cart_model.layoutChanged.connect(self.update_summary)
        self.cart_table_view.setModel(self.cart_model)
        self.cart_table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        left_layout.addWidget(self.cart_table_view)

        right_layout = QVBoxLayout()
        right_layout.setFixedWidth(300)

        summary_form = QFormLayout()
        self.subtotal_label = QLabel("$0.00")
        self.tax_input = QLineEdit("0.0")
        self.tax_input.textChanged.connect(self.update_summary)
        self.discount_input = QLineEdit("0.0")
        self.discount_input.textChanged.connect(self.update_summary)
        self.total_label = QLabel("$0.00")
        self.total_label.setStyleSheet("font-size: 18px; font-weight: bold;")

        summary_form.addRow("Subtotal:", self.subtotal_label)
        summary_form.addRow("Tax:", self.tax_input)
        summary_form.addRow("Discount:", self.discount_input)
        summary_form.addRow("Total:", self.total_label)
        right_layout.addLayout(summary_form)

        right_layout.addStretch()

        self.finalize_button = QPushButton("Finalize Sale")
        self.finalize_button.clicked.connect(self.finalize_sale)
        self.finalize_button.setStyleSheet("font-size: 18px; padding: 10px;")
        right_layout.addWidget(self.finalize_button)

        self.main_layout.addLayout(left_layout, 2)
        self.main_layout.addLayout(right_layout, 1)

    def add_product_to_cart(self):
        product_id_str = self.product_input.text()
        if not product_id_str.isdigit():
            QMessageBox.warning(self, "Invalid Input", "Product ID must be a number.")
            return

        product_id = int(product_id_str)
        db_session = SessionLocal()
        try:
            product = product_service.get_product(db_session, product_id)
            if product:
                self.cart_model.add_item(product, 1)
                self.product_input.clear()
            else:
                QMessageBox.warning(self, "Not Found", "Product not found.")
        finally:
            db_session.close()

    def update_summary(self):
        subtotal = self.cart_model.get_cart_total()
        tax = float(self.tax_input.text()) if self.tax_input.text() else 0
        discount = float(self.discount_input.text()) if self.discount_input.text() else 0
        total = subtotal + tax - discount

        self.subtotal_label.setText(f"${subtotal:.2f}")
        self.total_label.setText(f"${total:.2f}")

    def finalize_sale(self):
        cart_items = self.cart_model.get_cart_items()
        if not cart_items:
            QMessageBox.warning(self, "Empty Cart", "Cannot finalize an empty sale.")
            return

        # In a real app, you would select a customer. For now, use a default.
        db_session = SessionLocal()
        try:
            customer = db_session.query(customer_service.models.Customer).first()
            if not customer:
                QMessageBox.critical(self, "Error", "No customers in database. Please add a customer first.")
                return

            sale_data = {
                "customer_id": customer.id,
                "items": cart_items,
                "payment_type": "Cash", # Placeholder
                "tax": float(self.tax_input.text()),
                "discount": float(self.discount_input.text()),
            }

            new_sale = sales_service.create_sale(db_session, **sale_data)

            reply = QMessageBox.information(
                self, "Success", f"Sale #{new_sale.id} finalized successfully.",
                QMessageBox.Ok | QMessageBox.Save, QMessageBox.Ok
            )

            if reply == QMessageBox.Save:
                self.generate_invoice_pdf(new_sale)

            # Clear cart for next sale
            self.cart_model.clear_cart()
            self.tax_input.setText("0.0")
            self.discount_input.setText("0.0")

        except ValueError as e:
            QMessageBox.critical(self, "Error", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {e}")
        finally:
            db_session.close()

    def generate_invoice_pdf(self, sale: sales_service.models.Sale):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Invoice", f"invoice_{sale.id}.pdf", "PDF Files (*.pdf)")
        if not file_path:
            return

        c = canvas.Canvas(file_path, pagesize=letter)
        width, height = letter

        c.setFont("Helvetica-Bold", 18)
        c.drawString(1 * inch, height - 1 * inch, f"Invoice #{sale.id}")

        c.setFont("Helvetica", 12)
        c.drawString(1 * inch, height - 1.25 * inch, f"Date: {sale.date.strftime('%Y-%m-%d %H:%M')}")
        c.drawString(1 * inch, height - 1.5 * inch, f"Customer: {sale.customer.name}")

        text_y = height - 2.5 * inch
        c.setFont("Helvetica-Bold", 12)
        c.drawString(1 * inch, text_y, "Product")
        c.drawString(4 * inch, text_y, "Qty")
        c.drawString(5 * inch, text_y, "Unit Price")
        c.drawString(6 * inch, text_y, "Total")
        c.line(1 * inch, text_y - 5, width - 1 * inch, text_y - 5)

        text_y -= 20
        c.setFont("Helvetica", 12)
        for item in sale.sale_items:
            c.drawString(1 * inch, text_y, item.product.name)
            c.drawString(4.1 * inch, text_y, str(item.qty))
            c.drawString(5.1 * inch, text_y, f"${item.price:.2f}")
            c.drawString(6.1 * inch, text_y, f"${(item.price * item.qty):.2f}")
            text_y -= 20

        text_y -= 20
        c.line(4 * inch, text_y, width - 1 * inch, text_y)
        text_y -= 20

        c.drawString(5 * inch, text_y, "Subtotal:")
        c.drawString(6.1 * inch, text_y, f"${(sale.total - sale.tax + sale.discount):.2f}")
        text_y -= 20
        c.drawString(5 * inch, text_y, "Tax:")
        c.drawString(6.1 * inch, text_y, f"${sale.tax:.2f}")
        text_y -= 20
        c.drawString(5 * inch, text_y, "Discount:")
        c.drawString(6.1 * inch, text_y, f"-${sale.discount:.2f}")
        text_y -= 20
        c.setFont("Helvetica-Bold", 14)
        c.drawString(5 * inch, text_y, "Total:")
        c.drawString(6.1 * inch, text_y, f"${sale.total:.2f}")

        c.save()
        QMessageBox.information(self, "Success", f"Successfully saved invoice to {file_path}")
