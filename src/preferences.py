import logging
import os

PREFERENCES_FILE = "preferred.txt"

def load_preferences():
    """Load preferred cities from a file."""
    if not os.path.exists(PREFERENCES_FILE):
        logging.info("No file was found, creating a new one.")
        return []

    with open(PREFERENCES_FILE, "r") as file:
        return [line.strip() for line in file]

def save_preferences(preferences):
    """Saves preferred cities to a file."""
    with open(PREFERENCES_FILE, "w") as file:
        file.write("\n".join(preferences))