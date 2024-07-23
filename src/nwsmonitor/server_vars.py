"""Handler for server variables."""

import json
import logging
from typing import Any

log = logging.getLogger(__name__)
json_file = "serverVars.json"


def write(var_name: str, value: Any, guild: int) -> None:
    # if the json file exists, load it, otherwise initialize a blank dict
    try:
        with open(json_file, "r") as f:
            data = json.load(f)
    except (FileNotFoundError, ValueError):
        data = {}
    if data.get(guild) is not None:
        server_data = data[guild]
        server_data[var_name] = value
    else:
        try:
            data[guild][var_name] = value
        except (KeyError, TypeError):
            data[guild] = {var_name: value}
    with open(json_file, "w") as f:
        f.write(json.dumps(data, indent=4))


def get(var_name: str, guild: int) -> Any:
    try:
        with open(json_file, "r") as f:
            data = json.load(f)
    except (FileNotFoundError, ValueError):
        log.warning("Cannot open JSON file")
        return None
    if data.get(guild) is not None:
        server_data = data[guild]
        value = server_data.get(var_name)
        return value
    return None


def remove_guild(guild: int) -> None:
    try:
        with open(json_file, "r") as f:
            data = json.load(f)
    except (FileNotFoundError, ValueError):
        log.warning("Cannot open JSON file")
        return None
    try:
        del data[guild]
    except KeyError:
        log.warning("Attempted to remove a guild that does not exist.")
    else:
        with open(json_file, "w") as f:
            f.write(json.dumps(data, indent=4))
