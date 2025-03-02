import os
import json
from pathlib import Path

# Ensure the uploads folder and config file exist
DOCUMENTS_PATH = str(Path(os.path.expanduser("~")) / "Documents")
CONFIG_FOLDER = os.path.join(DOCUMENTS_PATH, "PcDrop")
CONFIG_FILE = os.path.join(CONFIG_FOLDER, "config.json")

# Create the necessary directories if they don't exist
os.makedirs(CONFIG_FOLDER, exist_ok=True)

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_config(data):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(data, f)

# Default configurations
config = load_config()
upload_directory = config.get("upload_directory", str(Path(os.path.expanduser("~")) / "Pictures"))
shared_directory = config.get("shared_directory", str(Path(os.path.expanduser("~")) / "Documents"))