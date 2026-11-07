# Parsing helpers for shot data: paths, JSON content and JSON field navigation.
# Pure functions with no MCP or GOLEM client dependencies, so they can be used
# directly in analysis code without running the server.

import json
from urllib.parse import unquote, urlparse


def cleanse_path(url: str) -> str:
    """Turns a user-supplied path or URL into a plain relative path (drops query, '..' and percent-encoding)."""
    return urlparse(unquote(url)).path.replace("..", "")


def split_field_path(fieldPath: str) -> list[str]:
    """Splits a '/'-separated field path into its non-empty segments."""
    return [field for field in fieldPath.strip("/").split("/") if field]


def parse_json(data):
    """Parses str/bytes JSON content. Already-parsed data is returned unchanged."""
    if isinstance(data, (str, bytes, bytearray)):
        return json.loads(data)
    return data


def get_field(value, fieldPath: str):
    """Walks dict keys and list indices along fieldPath.

    Raises KeyError, IndexError, TypeError or ValueError when the path does not exist.
    """
    for field in split_field_path(fieldPath):
        if isinstance(value, dict):
            value = value[field]
        elif isinstance(value, list):
            value = value[int(field)]
        else:
            raise KeyError(field)
    return value


def child_fields(value) -> list[str]:
    """Shallow list of child keys (dict) or indices (list) as strings. Other values have none."""
    if isinstance(value, dict):
        return list(value.keys())
    if isinstance(value, list):
        return [str(i) for i in range(len(value))]
    return []


# Shot-level JSON access. `source` is any object with getShotFileCached(shotID, filePath),
# e.g. a GolemCLIENThttp or GolemCLIENTlocal instance. Paths must already be cleansed.
# They raise from failures.
def getShotJSONfield(source, shotID: int, filePath: str, fieldPath: str):
    """Value at fieldPath inside the JSON file filePath of shot shotID."""
    return get_field(parse_json(source.getShotFileCached(shotID, filePath)), fieldPath)
def listJSONfields(source, shotID: int, filePath: str, fieldPath: str) -> list[str]:
    """Shallow child fields of the value at fieldPath inside the JSON file filePath of shot shotID."""
    return child_fields(getShotJSONfield(source, shotID, filePath, fieldPath))
