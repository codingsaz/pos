import sys
from PySide6.QtWidgets import QApplication
from optical_store_pos.db.database import setup_database
from optical_store_pos.ui.main_window import MainWindow

def main():
    # Setup the database
    setup_database()

    # Create the application
    app = QApplication(sys.argv)

    # Create and show the main window
    window = MainWindow()
    window.show()

    # Start the event loop
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
