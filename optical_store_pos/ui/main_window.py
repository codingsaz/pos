from PySide6.QtWidgets import QMainWindow, QTabWidget
from optical_store_pos.ui.customer_view import CustomerView

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Optical Store POS")
        self.setGeometry(100, 100, 800, 600)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.customer_tab = CustomerView()
        self.tabs.addTab(self.customer_tab, "Customers")
