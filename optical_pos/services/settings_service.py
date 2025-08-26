import json
from pathlib import Path
from typing import Dict, Any

# Define the path to the settings file relative to the project root.
# Assuming the project root is the parent of the 'services' directory.
SETTINGS_FILE = Path(__file__).parent.parent / "data" / "settings.json"

DEFAULT_SETTINGS = {
    "shop_name": "My Optical Store",
    "tax_percent": 8.0,
    "currency_symbol": "$",
    "logo_path": ""
}

def load_settings() -> Dict[str, Any]:
    """
    Loads settings from the settings.json file.
    If the file doesn't exist, it creates it with default values.
    """
    if not SETTINGS_FILE.exists():
        save_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS

    try:
        with open(SETTINGS_FILE, 'r') as f:
            settings = json.load(f)
            # Ensure all default keys are present
            for key, value in DEFAULT_SETTINGS.items():
                settings.setdefault(key, value)
            return settings
    except (json.JSONDecodeError, IOError):
        # If file is corrupted or unreadable, return defaults
        return DEFAULT_SETTINGS

def save_settings(settings: Dict[str, Any]):
    """
    Saves the provided settings dictionary to the settings.json file.
    """
    try:
        SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f, indent=4)
    except IOError as e:
        print(f"Error saving settings: {e}")

# Initialize settings on first import
settings_cache = load_settings()

def get_setting(key: str) -> Any:
    """Gets a single setting value from the cached settings."""
    return settings_cache.get(key, DEFAULT_SETTINGS.get(key))

def update_setting(key: str, value: Any):
    """Updates a single setting and saves all settings."""
    global settings_cache
    settings_cache[key] = value
    save_settings(settings_cache)
