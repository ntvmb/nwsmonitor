"""Handler for global variables."""

import json
import logging

log = logging.getLogger(__name__)
json_file = "globalVars.json"


def write(var_name: str, value):
    try:
        with open(json_file, "r") as f:
            data = json.load(f)
    except (FileNotFoundError, ValueError):
        data = {}
    data[var_name] = value
    with open(json_file, "w") as f:
        f.write(json.dumps(data, indent=4))


def get(var_name: str):
    try:
        with open(json_file, "r") as f:
            data = json.load(f)
    except (FileNotFoundError, ValueError):
        log.warning("Cannot open JSON file")
        return None
    value = data.get(var_name)
    return value
