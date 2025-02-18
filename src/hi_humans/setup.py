import os
import uuid
import re
import shutil
import logging
import platform
import requests
from pathlib import Path

# Google Analytics 4 Configuration
GA_MEASUREMENT_ID = "G-JSXPLJ0P6M"  # Your GA4 Measurement ID
GA_API_SECRET = "40wcO2OLQty3WMtj3BLxKw"  # Replace with your GA API Secret
GA_TRACKING_URL = f"https://www.google-analytics.com/mp/collect?measurement_id={GA_MEASUREMENT_ID}&api_secret={GA_API_SECRET}"

# Configure logging for clearer output
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def update_shell_config(serial_number: str, config_path: Path) -> None:
    """
    Update the given shell configuration file with the new serial number.
    A backup of the file is created before modifying it.
    """
    backup_path = config_path.with_suffix(config_path.suffix + ".bak")
    try:
        if config_path.exists():
            shutil.copy(config_path, backup_path)
            logging.info(f"Backup created at {backup_path}")
    except Exception as e:
        logging.warning(f"Could not create a backup for {config_path}: {e}")

    content = config_path.read_text() if config_path.exists() else ""
    pattern = re.compile(r"^export MY_PACKAGE_SERIAL=.*$", re.MULTILINE)
    
    if pattern.search(content):
        new_content = pattern.sub(f"export MY_PACKAGE_SERIAL='{serial_number}'", content)
        logging.info(f"Existing serial number updated in {config_path}.")
    else:
        new_content = content + f"\n# Serial Number for my_package\nexport MY_PACKAGE_SERIAL='{serial_number}'\n"
        logging.info(f"Serial number appended to {config_path}.")
    
    config_path.write_text(new_content)

def track_installation(serial_number: str) -> None:
    """
    Send installation data to Google Analytics 4.
    """
    data = {
        "client_id": serial_number,
        "events": [{
            "name": "python_package_install",
            "params": {
                "serial_number": serial_number,
                "os": platform.system(),
                "version": platform.release(),
                "hostname": platform.node()
            }
        }]
    }

    try:
        response = requests.post(GA_TRACKING_URL, json=data)
        if response.status_code == 200:
            logging.info("Installation tracked via Google Analytics.")
        else:
            logging.warning(f"Failed to track installation. Status code: {response.status_code}")
    except Exception as e:
        logging.warning(f"Tracking failed: {e}")

def main():
    # Generate a new UUID as a serial number
    serial_number = str(uuid.uuid4())
    logging.info(f"Generated serial number: {serial_number}")
    
    # Define shell configuration files using pathlib
    home = Path.home()
    bashrc = home / ".bashrc"
    bash_profile = home / ".bash_profile"
    zshrc = home / ".zshrc"
    
    # Check for existing configuration files
    config_files = [bashrc, bash_profile, zshrc]
    existing_configs = [cfg for cfg in config_files if cfg.exists()]
    
    if not existing_configs:
        # If no config exists, default to .bashrc
        existing_configs.append(bashrc)
        logging.info("No existing shell configuration files found. Creating ~/.bashrc")
    
    # Update each configuration file with the serial number
    for config in existing_configs:
        update_shell_config(serial_number, config)

    # Track the installation with Google Analytics
    track_installation(serial_number)
    
    logging.info(f"\nSerial Number set as an environment variable: {serial_number}")
    logging.info("To apply changes, please run 'source <config_file>' (e.g., 'source ~/.bashrc') or open a new terminal.")

if __name__ == "_main_":
    main()
