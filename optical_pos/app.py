import sys
from PySide6.QtWidgets import QApplication
from optical_pos.ui.screens.auth import LoginScreen
from optical_pos.ui.main_window import MainWindow
from optical_pos.db.seed import seed_data, init_db

class AppController:
    """
    Manages the application flow, switching between login screen and main window.
    """
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.session_info = None
        self.main_window = None

        # Initialize and seed the database on first run
        print("Initializing database...")
        init_db()
        seed_data()
        print("Database setup complete.")

        self.login_screen = LoginScreen()
        self.login_screen.login_successful.connect(self.on_login_success)

    def run(self):
        """
        Starts the application by showing the login screen.
        """
        print("Showing login screen.")
        self.login_screen.show()
        sys.exit(self.app.exec())

    def on_login_success(self, session_info: dict):
        """
        Slot for the login_successful signal.
        Stores session info and shows the main window.
        """
        self.session_info = session_info
        print(f"Login successful! User: {self.session_info['username']}, Role: {self.session_info['role']}")

        # The login screen closes itself, now show the main window
        self.main_window = MainWindow(session_info=self.session_info)
        self.main_window.show()

if __name__ == "__main__":
    controller = AppController()
    controller.run()
