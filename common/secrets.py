"""Manage secrets files"""
# INFO: Manage secrets files
import json
from pathlib import Path
import os


def load(topic: str, file: str = "credentials.json"):
    """Load secrets from `~/.config/<topic>/<file>`"""
    home = str(Path.home())
    with open(os.path.join(home, ".config", topic, file)) as json_file:
        data = json.load(json_file)
    return data
