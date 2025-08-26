from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTableView,
    QPushButton,
    QLabel,
    QGroupBox,
    QHeaderView,
)
from PySide6.QtCore import QAbstractTableModel, Qt, QModelIndex
from typing import List, Any
from optical_pos.db.models import InventoryMovement, Product
from optical_pos.services import inventory_service
from optical_pos.db.database import SessionLocal

class MovementTableModel(QAbstractTableModel):
    def __init__(self, data: List[InventoryMovement]):
        super().__init__()
        self._data = data
        self.headers = ["Date", "Product", "Qty Change", "Reason"]

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self._data)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self.headers)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        if role == Qt.DisplayRole:
            movement = self._data[index.row()]
            return [
                movement.date.strftime("%Y-%m-%d %H:%M"),
                movement.product.name,
                str(movement.qty_change),
                movement.reason
            ][index.column()]
        return None

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole) -> Any:
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.headers[section]
        return None

class LowStockTableModel(QAbstractTableModel):
    def __init__(self, data: List[Product]):
        super().__init__()
        self._data = data
        self.headers = ["Product Name", "Category", "Current Stock"]

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self._data)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self.headers)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        if role == Qt.DisplayRole:
            product = self._data[index.row()]
            return [product.name, product.category, str(product.stock_qty)][index.column()]
        return None

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole) -> Any:
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.headers[section]
        return None

class InventoryScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.main_layout = QVBoxLayout(self)

        title_label = QLabel("Inventory Management")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        self.main_layout.addWidget(title_label)

        # --- Top layout for alerts and actions ---
        top_layout = QHBoxLayout()

        # Low Stock Alerts
        low_stock_group = QGroupBox("Low Stock Alerts (Threshold: 10)")
        low_stock_layout = QVBoxLayout(low_stock_group)
        self.low_stock_table = QTableView()
        self.low_stock_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        low_stock_layout.addWidget(self.low_stock_table)
        top_layout.addWidget(low_stock_group)

        # Actions
        actions_group = QGroupBox("Actions")
        actions_layout = QVBoxLayout(actions_group)
        self.reorder_button = QPushButton("Generate Reorder Suggestion")
        self.po_button = QPushButton("New Purchase Order")
        actions_layout.addWidget(self.reorder_button)
        actions_layout.addWidget(self.po_button)
        actions_layout.addStretch()
        top_layout.addWidget(actions_group)

        self.main_layout.addLayout(top_layout)

        # --- Bottom layout for all movements ---
        movements_group = QGroupBox("All Stock Movements")
        movements_layout = QVBoxLayout(movements_group)
        self.movements_table = QTableView()
        self.movements_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        movements_layout.addWidget(self.movements_table)
        self.main_layout.addWidget(movements_group)

        self.load_data()

    def load_data(self):
        db_session = SessionLocal()
        try:
            # Load all movements
            # In a real app, this should be paginated
            all_movements = db_session.query(InventoryMovement).order_by(InventoryMovement.date.desc()).all()
            self.movements_table.setModel(MovementTableModel(all_movements))

            # Load low stock items
            low_stock_products = inventory_service.get_low_stock_products(db_session, threshold=10)
            self.low_stock_table.setModel(LowStockTableModel(low_stock_products))
        finally:
            db_session.close()
