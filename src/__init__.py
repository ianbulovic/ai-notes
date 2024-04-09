import json
import os
import tomllib

with open("config.toml", "rb") as f:
    CONFIG = tomllib.load(f)

NOTES_DIR = "debug-notes" if CONFIG["settings"]["debug"] else "notes"
TAGS_FILE = os.path.join(NOTES_DIR, "tags.json")

if not os.path.exists(NOTES_DIR):
    os.makedirs(NOTES_DIR)

if not os.path.exists(TAGS_FILE):
    with open(TAGS_FILE, "w") as f:
        json.dump([], f)
