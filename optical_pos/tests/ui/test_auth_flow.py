import pytest
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from optical_pos.app import AppController

# Mark this module as requiring a Qt event loop
pytestmark = pytest.mark.qt

def test_login_flow_success(qtbot):
    """
    Tests the full login flow from showing the login screen to opening the main window.
    """
    # The AppController initializes the DB and seeds it
    app_controller = AppController()

    # The login screen should be visible initially
    qtbot.addWidget(app_controller.login_screen)
    assert app_controller.login_screen.isVisible()
    assert app_controller.main_window is None

    # Simulate user input
    qtbot.keyClicks(app_controller.login_screen.username_input, "admin")
    qtbot.keyClicks(app_controller.login_screen.password_input, "admin123")

    # Simulate button click
    qtbot.mouseClick(app_controller.login_screen.login_button, Qt.LeftButton)

    # Wait until the main window is created and visible
    def check_main_window_visible():
        assert app_controller.main_window is not None
        assert app_controller.main_window.isVisible()
        # Also check that the login screen is now closed
        assert not app_controller.login_screen.isVisible()

    qtbot.waitUntil(check_main_window_visible, timeout=5000)

    # Final check on the session info
    assert app_controller.session_info is not None
    assert app_controller.session_info['username'] == 'admin'
    assert app_controller.session_info['role'] == 'Admin'

def test_login_flow_failure(qtbot):
    """
    Tests that the main window does not open with incorrect credentials.
    """
    app_controller = AppController()

    qtbot.addWidget(app_controller.login_screen)

    # Simulate incorrect user input
    qtbot.keyClicks(app_controller.login_screen.username_input, "admin")
    qtbot.keyClicks(app_controller.login_screen.password_input, "wrongpassword")

    # Simulate button click
    qtbot.mouseClick(app_controller.login_screen.login_button, Qt.LeftButton)

    # The main window should NOT appear
    assert app_controller.main_window is None

    # The login screen should still be visible
    assert app_controller.login_screen.isVisible()

    # In a real test, we would also check for the error message box,
    # but that requires more complex handling of modal dialogs in tests.
    # For now, we confirm the state did not change as expected.
