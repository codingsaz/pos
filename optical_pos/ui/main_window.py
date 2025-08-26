import os
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QStackedWidget,
    QComboBox,
    QLabel,
    QApplication,
)
from PySide6.QtCore import QFile, QTextStream
from optical_pos.ui.widgets.nav_sidebar import NavSidebar
from optical_pos.ui.screens.dashboard import DashboardScreen

class MainWindow(QMainWindow):
    def __init__(self, session_info: dict):
        super().__init__()
        self.session_info = session_info
        self.setWindowTitle(f"Optical Store POS - Logged in as {self.session_info['username']} ({self.session_info['role']})")
        self.setGeometry(100, 100, 1200, 800)

        # Main widget and layout
        self.main_widget = QWidget()
        self.main_layout = QHBoxLayout(self.main_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setCentralWidget(self.main_widget)

        # Sidebar
        self.sidebar = NavSidebar()
        self.main_layout.addWidget(self.sidebar)

        # Content area using QStackedWidget
        self.content_stack = QStackedWidget()
        self.main_layout.addWidget(self.content_stack)

        # Create and add pages to the stack
        self.pages = {
            "dashboard": DashboardScreen(),
            "customers": self._create_placeholder_page("Customers"),
            "products": self._create_placeholder_page("Products"),
            "sales": self._create_placeholder_page("Sales"),
            "reports": self._create_placeholder_page("Reports"),
            "inventory": self._create_placeholder_page("Inventory"),
            "settings": self._create_placeholder_page("Settings")
        }
        for widget in self.pages.values():
            self.content_stack.addWidget(widget)

        # Connect sidebar signals to switch pages
        self.sidebar.screen_changed.connect(self.switch_screen)

        # --- Theme Switcher ---
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark"])
        self.theme_combo.currentTextChanged.connect(self.switch_theme)

        # Add theme switcher to the bottom of the sidebar
        self.sidebar.main_layout.addStretch()
        theme_label = QLabel("Theme:")
        self.sidebar.main_layout.addWidget(theme_label)
        self.sidebar.main_layout.addWidget(self.theme_combo)

        # Set initial theme
        self.switch_theme("Light")

    def _create_placeholder_page(self, name: str) -> QWidget:
        """Helper to create a placeholder widget for a screen."""
        widget = QWidget()
        layout = QHBoxLayout()
        layout.addWidget(QLabel(f"This is the {name} screen."))
        widget.setLayout(layout)
        return widget

    def switch_screen(self, screen_id: str):
        """Slot to change the visible screen in the QStackedWidget."""
        if screen_id in self.pages:
            self.content_stack.setCurrentWidget(self.pages[screen_id])
            print(f"Switched to {screen_id} screen.")

    def switch_theme(self, theme_name: str):
        """Loads and applies a QSS theme file."""
        theme_filename = f"optical_pos/ui/theme/{theme_name.lower()}.qss"
        try:
            with open(theme_filename, "r") as f:
                style_sheet = f.read()
                QApplication.instance().setStyleSheet(style_sheet)
                print(f"Applied {theme_name} theme.")
        except FileNotFoundError:
            print(f"Warning: Theme file not found at {theme_filename}")
            # Apply a default empty stylesheet to clear any previous theme
            QApplication.instance().setStyleSheet("")
