@echo off
echo --- Setting up Python virtual environment... ---
if not exist .venv (
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo Error: Failed to create virtual environment. Please ensure python is installed and in your PATH.
        exit /b 1
    )
)

echo --- Activating virtual environment... ---
call .venv\Scripts\activate.bat

echo --- Installing dependencies from requirements.txt... ---
pip install -r optical_pos\requirements.txt
if %errorlevel% neq 0 (
    echo Error: Failed to install dependencies.
    exit /b 1
)

echo --- Starting Optical POS Application... ---
python optical_pos\app.py
