# Optical Store POS

This is a desktop application for managing an optical store, built with PySide6.

## Features

- Customer Management
- Product Management
- Prescription Management
- Sales and Billing
- Inventory Tracking
- Reporting
- and more...

## Getting Started

### Easy Run (Recommended)

Simply run the script for your operating system. It will create a virtual environment, install dependencies, and launch the application automatically.

-   On **Windows**: From the project's root directory, double-click `run.bat` or run it from the command prompt:
    ```sh
    run.bat
    ```
-   On **macOS/Linux**: From the project's root directory, make the script executable first, then run it:
    ```sh
    chmod +x run.sh
    ./run.sh
    ```

### Manual Installation

If you prefer to set up the environment manually:

1.  **Clone the repository**
2.  **Create a virtual environment**: `python -m venv .venv`
3.  **Activate the virtual environment**:
    -   Windows: `call .venv\Scripts\activate.bat`
    -   macOS/Linux: `source .venv/bin/activate`
4.  **Install the dependencies**: `pip install -r requirements.txt`
5.  **Run the application**: `python app.py`

The default admin login is:
-   **Username**: `admin`
-   **Password**: `admin123`

## Building from Source (Windows)

To create a distributable `.exe` installer for Windows, you will need to have PyInstaller and Inno Setup installed.

1.  **Install PyInstaller**:
    ```sh
    pip install pyinstaller
    ```
2.  **Install Inno Setup**:
    Download and install the latest version of Inno Setup from [jrsoftware.org](https://jrsoftware.org/isinfo.php).

3.  **Build the Executable**:
    Run PyInstaller from the `optical_pos` directory using the provided spec file.
    ```sh
    pyinstaller build.spec
    ```
    This will create a `dist/OpticalPOS` folder with the executable and all its dependencies.

4.  **Build the Installer**:
    Right-click on the `scripts/setup.iss` file and select "Compile". This will use Inno Setup to create a single `OpticalPOS-1.0-setup.exe` file in the `scripts/Output` directory.

## Screenshots

*(Placeholder for Login Screen Screenshot)*
![Login Screen](path/to/login_screen.png)

*(Placeholder for Dashboard Screenshot)*
![Dashboard](path/to/dashboard.png)

*(Placeholder for POS Screen Screenshot)*
![POS Screen](path/to/pos_screen.png)
