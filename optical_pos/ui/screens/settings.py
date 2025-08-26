import shutil
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTabWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QFormLayout,
    QFileDialog,
    QMessageBox,
)
from optical_pos.services import settings_service
from optical_pos.db.database import DB_FILE # Get the DB file path

class SettingsScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.main_layout = QVBoxLayout(self)

        title_label = QLabel("Settings & Store Management")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        self.main_layout.addWidget(title_label)

        self.tabs = QTabWidget()
        self.main_layout.addWidget(self.tabs)

        # Create tabs
        self.shop_info_tab = QWidget()
        self.user_management_tab = QWidget() # Placeholder for now
        self.data_tab = QWidget()

        self.tabs.addTab(self.shop_info_tab, "Shop Info")
        self.tabs.addTab(self.user_management_tab, "User Management")
        self.tabs.addTab(self.data_tab, "Data Management")

        # Populate tabs
        self._populate_shop_info_tab()
        self._populate_data_tab()
        self._populate_user_management_tab() # Will be a placeholder

    def _populate_shop_info_tab(self):
        layout = QFormLayout(self.shop_info_tab)

        self.shop_name_input = QLineEdit()
        self.tax_input = QLineEdit()
        self.currency_input = QLineEdit()

        layout.addRow("Shop Name:", self.shop_name_input)
        layout.addRow("Tax Rate (%):", self.tax_input)
        layout.addRow("Currency Symbol:", self.currency_input)

        self.save_button = QPushButton("Save Settings")
        self.save_button.clicked.connect(self.save_shop_info)
        layout.addRow(self.save_button)

        self.load_shop_info()

    def _populate_data_tab(self):
        layout = QVBoxLayout(self.data_tab)

        backup_button = QPushButton("Backup Database")
        backup_button.clicked.connect(self.backup_database)

        restore_button = QPushButton("Restore Database")
        restore_button.clicked.connect(self.restore_database)

        layout.addWidget(backup_button)
        layout.addWidget(restore_button)
        layout.addStretch()

    def _populate_user_management_tab(self):
        layout = QVBoxLayout(self.user_management_tab)
        label = QLabel("User management UI will be here.")
        layout.addWidget(label)

    def load_shop_info(self):
        """Loads settings and populates the form fields."""
        settings = settings_service.load_settings()
        self.shop_name_input.setText(settings.get("shop_name", ""))
        self.tax_input.setText(str(settings.get("tax_percent", 0.0)))
        self.currency_input.setText(settings.get("currency_symbol", "$"))

    def save_shop_info(self):
        """Saves the shop info settings."""
        try:
            settings = {
                "shop_name": self.shop_name_input.text(),
                "tax_percent": float(self.tax_input.text()),
                "currency_symbol": self.currency_input.text(),
            }
            # Preserve other settings that might exist
            current_settings = settings_service.load_settings()
            current_settings.update(settings)

            settings_service.save_settings(current_settings)
            QMessageBox.information(self, "Success", "Settings saved successfully.")
        except ValueError:
            QMessageBox.critical(self, "Error", "Invalid input. Tax rate must be a number.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not save settings: {e}")

    def backup_database(self):
        """Backs up the SQLite database file."""
        backup_path, _ = QFileDialog.getSaveFileName(self, "Backup Database", "optical_pos_backup.sqlite", "SQLite Database Files (*.sqlite)")
        if not backup_path:
            return

        try:
            shutil.copy(DB_FILE, backup_path)
            QMessageBox.information(self, "Success", f"Database successfully backed up to {backup_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not back up database: {e}")

    def restore_database(self):
        """Restores the database from a backup file."""
        reply = QMessageBox.warning(
            self, "Confirm Restore",
            "Restoring the database will overwrite all current data. This cannot be undone. Are you sure you want to continue?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.No:
            return

        backup_path, _ = QFileDialog.getOpenFileName(self, "Restore Database", "", "SQLite Database Files (*.sqlite)")
        if not backup_path:
            return

        try:
            # In a real app, you should close all DB connections before doing this.
            # For this simple case, we just copy the file.
            shutil.copy(backup_path, DB_FILE)
            QMessageBox.information(self, "Success", "Database successfully restored. Please restart the application for changes to take effect.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not restore database: {e}")
