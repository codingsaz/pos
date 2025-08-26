from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox,
)
from PySide6.QtCore import Signal
from optical_pos.services import auth_service
from optical_pos.db.database import SessionLocal

class LoginScreen(QWidget):
    # Signal to be emitted on successful login
    login_successful = Signal(dict)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login - Optical POS")
        self.setGeometry(300, 300, 300, 150)

        layout = QVBoxLayout()

        self.username_label = QLabel("Username:")
        self.username_input = QLineEdit()
        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)

        self.password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)

        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.handle_login)
        layout.addWidget(self.login_button)

        self.setLayout(layout)

    def handle_login(self):
        """
        Handles the login button click.
        Authenticates the user and emits a signal on success.
        """
        username = self.username_input.text()
        password = self.password_input.text()

        if not username or not password:
            QMessageBox.warning(self, "Login Failed", "Username and password are required.")
            return

        db_session = SessionLocal()
        try:
            user = auth_service.authenticate_user(db_session, username, password)
            if user:
                # On successful login, emit the signal with user info
                self.login_successful.emit({"username": user.username, "role": user.role})
                self.close() # Close the login window
            else:
                QMessageBox.warning(self, "Login Failed", "Invalid username or password.")
        finally:
            db_session.close()
