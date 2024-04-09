from datetime import datetime, timedelta
import os
from pathvalidate import validate_filename, ValidationError
import random


def note_exists(dir, name):
    """Check if a note with the given name exists in the given directory."""
    return os.path.exists(os.path.join(dir, f"{name}.json"))


def is_valid_filename(fname: str):
    """Check if the given filename is valid."""
    try:
        validate_filename(fname)
        return True
    except ValidationError:
        return False


def get_default_note_title(dir: str, base_title: str):
    """
    Get a default note title based on the given base title.
    If a note with the base title already exists, append a number to the title.
    """
    assert is_valid_filename(f"{base_title}.json")

    if not note_exists(dir, base_title):
        return base_title

    i = 2
    while note_exists(dir, f"{base_title} ({i})"):
        i += 1
    return f"{base_title} ({i})"


def smart_datetime_string(dt: datetime):
    """
    Get a human-readable string representation of the given datetime.
    """
    now = datetime.now()
    if dt.date() == now.date():
        if now - dt < timedelta(minutes=1):
            return "Just now"
        elif now - dt < timedelta(hours=1):
            return f"{(now - dt).seconds // 60} minutes ago"
        else:
            return dt.strftime("%I:%M %p")
    elif dt.date() == now.date() - timedelta(days=1):
        return f"Yesterday at {dt.strftime('%I:%M %p')}"
    else:
        return dt.strftime("%m/%d/%Y at %I:%M %p")


def generate_random_hex_color() -> str:
    """Generate a random color in hex format."""
    return f"#{random.randint(0, 255):02x}{random.randint(0, 255):02x}{random.randint(0, 255):02x}"
