from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton
from PySide6.QtCore import Signal

class NavSidebar(QWidget):
    """
    A navigation sidebar widget with buttons to switch between screens.
    """
    # Signal to be emitted when a navigation button is clicked
    # It will carry the name of the screen to switch to (e.g., "Dashboard")
    screen_changed = Signal(str)

    def __init__(self):
        super().__init__()
        self.setFixedWidth(150) # Set a fixed width for the sidebar

        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(5, 5, 5, 5)
        self.main_layout.setSpacing(10)

        # --- Navigation Buttons ---
        nav_buttons_config = [
            ("Dashboard", "dashboard"),
            ("Customers", "customers"),
            ("Products", "products"),
            ("Prescriptions", "prescriptions"),
            ("Sales", "sales"),
            ("Reports", "reports"),
            ("Inventory", "inventory"),
            ("Settings", "settings"),
        ]

        for name, screen_id in nav_buttons_config:
            button = QPushButton(name)
            button.clicked.connect(lambda checked=False, sid=screen_id: self.screen_changed.emit(sid))
            self.main_layout.addWidget(button)

        self.main_layout.addStretch() # Pushes buttons to the top

        self.setLayout(self.main_layout)
