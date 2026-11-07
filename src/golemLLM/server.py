# MCP server, main

import asyncio
import json
import logging
import os
import time
from pathlib import Path
from urllib.parse import unquote, urlparse

from mcp.server.apps import Apps
from mcp.server.mcpserver import MCPServer
from mcp.types import CallToolResult, TextContent

from golemLLM.core.client import GolemCLIENThttp, GolemCLIENTlocal

INSTRUCTIONS = """You are a research assistant aiding the operator (user) in operating the GOLEM tokamak.
You may propose discharges inline with criteria of the operator's will, which may or may not be approved.
You may do so by sending a proposal to this MCP server.
Further instructions and experience in operating the tokamak may be found in guide://basics (see MCP resources)."""

LOCAL = False  # Use local GolemClient for shots?
CACHE_FILES = True
CLIENT_LOCAL_SHOTSDIR = "/home/tG/shots/"
CLIENT_HTTP_SHOTSURL = "http://golem.fjfi.cvut.cz/shots"
VERBOSE = False  # Verbose logging for GolemClient

KNOWLEDGE_BASICS = os.path.join(os.path.dirname(__file__), "guide", "basics.md")
KNOWLEDGE_STATUS = os.path.join(os.path.dirname(__file__), "guide", "status.md")

DRY_RUN = True  # Testing purposes only, prevents from running discharges
TTL = 3600  # Time a proposal is valid for [s]
AWAIT_TIMEOUT = 3600  # Max time awaitShot waits for a shot [s]
AWAIT_POLL_INTERVAL = 2  # Shot existence probe interval for awaitShot [s]
UI_URI = "ui://proposal.html"
UI_FILE = Path(__file__).parent / "ui" / "proposal.html"

LOGGER = logging.getLogger("MCPGolemLLM")
APPS = Apps()
GOLEMC = (GolemCLIENTlocal(CLIENT_LOCAL_SHOTSDIR, cache=CACHE_FILES, verbose=VERBOSE)
          if LOCAL else GolemCLIENThttp(CLIENT_HTTP_SHOTSURL, cache=CACHE_FILES, verbose=VERBOSE))

#region Helpers
def _error(error_type: str, message: str) -> dict:
    return {"status": "error", "error_type": error_type, "message": message}

def cleanseURL(url: str) -> str:
    return urlparse(unquote(url)).path.replace("..", "")

def _parse_shot_id(shotID):
    """Returns (shotID, None) or (None, error). Does not check existence."""
    try:
        return int(shotID), None
    except (ValueError, TypeError):
        return None, _error("INVALID_SHOT_ID", f"Invalid shotID '{shotID}'. Must be an integer.")

existence_cache = {}  # shotID -> True. Only positive results are cached, so a shot that appears later is still found.

def _shot_exists(shotID: int) -> bool:
    if shotID not in existence_cache:
        if not GOLEMC.shotProbeHEAD(shotID):
            return False
        existence_cache[shotID] = True
    return True

def _resolve_shot(shotID):
    """Validates the shot ID and checks that the shot exists. Shot 0 is never probed."""
    shotID, err = _parse_shot_id(shotID)
    if err:
        return None, err
    if shotID != 0 and not _shot_exists(shotID):
        return None, _error("SHOT_NOT_FOUND", f"Shot {shotID} not found.")
    return shotID, None

def _read_json_field(shotID: int, filepath: str, fieldPath: str):
    data = GOLEMC.getShotFileCached(shotID, filepath)
    if isinstance(data, (str, bytes, bytearray)):
        data = json.loads(data)

    value = data
    for field in fieldPath.strip("/").split("/"):
        if not field:
            continue
        if isinstance(value, dict):
            value = value[field]
        elif isinstance(value, list):
            value = value[int(field)]
        else:
            raise KeyError(field)
    return value

def _json_field_error(e: Exception, shotID: int, filepath: str, fieldPath: str) -> dict:
    # Order matters: JSONDecodeError and UnicodeDecodeError are also ValueErrors.
    if isinstance(e, FileNotFoundError):
        return _error("FILE_NOT_FOUND", f"File '{filepath}' not found for shot {shotID}.")
    if isinstance(e, (json.JSONDecodeError, UnicodeDecodeError)):
        return _error("INVALID_JSON", f"File '{filepath}' does not contain valid JSON.")
    if isinstance(e, (KeyError, IndexError, TypeError, ValueError)):
        return _error("FIELD_NOT_FOUND", f"Field path '{fieldPath}' not found in file '{filepath}'.")
    return _error("UNKNOWN_ERROR", f"Unknown error while reading field '{fieldPath}' from file '{filepath}' for shot {shotID}.")

def _read_knowledge(path: str):
    try:
        with open(path, "r") as f:
            return f.read()
    except FileNotFoundError:
        return _error("FILE_NOT_FOUND", "Knowledge file not found.")
#endregion

#region MCP application
@APPS.tool(resource_uri=UI_URI, name="proposeDischarge", description="Propose a discharge to the operator.")
def MCP_proposeDischarge(proposalTitle: str, proposalReason: str, referenceShotID: int, proposedCommand: str):
    try:
        referenceShotID = int(referenceShotID)
        if referenceShotID < 0:
            raise ValueError
    except (ValueError, TypeError):
        return _error("INVALID_SHOT_ID", f"Invalid referenceShotID '{referenceShotID}'. Must be a non-negative integer.")

    return CallToolResult(
        content=[TextContent(type="text",
                             text=(
                                 f"Proposal title: {proposalTitle}\n"
                                 f"Proposal reasoning: {proposalReason}\n"
                                 f"Parameter reference shot ID: {referenceShotID}\n"
                                 f"Proposed command: {proposedCommand}"
                             ))],
        structured_content={
            "proposal_title": proposalTitle,
            "proposal_reason": proposalReason,
            "reference_shot_ID": referenceShotID,
            "proposed_command": proposedCommand
        },
        _meta={"ui": {"resourceUri": UI_URI}}
    )

APPS.add_html_resource(
    UI_URI,
    UI_FILE.read_text(),
    name="Discharge proposal interface",
    description="Interface for proposing discharges to the operator.",
)

SERVER = MCPServer("GolemLLM", title="GOLEM AI discharge assistance toolkit", instructions=INSTRUCTIONS,
                   extensions=[APPS])
#endregion

#region GOLEM data access
@SERVER.tool("getShotFile", description="Get a file from a shot. File path is relative to the shot's root directory. Example: getShotFile(0, 'conductor/discharge.json')")
def MCP_getShotFile(shotID: int, filePath: str):
    filepath = cleanseURL(filePath)
    shotID, err = _resolve_shot(shotID)
    if err:
        return err

    try:
        data = GOLEMC.getShotFileCached(shotID, filepath)
    except FileNotFoundError:
        return _error("FILE_NOT_FOUND", f"File '{filepath}' not found for shot {shotID}.")
    except Exception:
        return _error("UNKNOWN_ERROR", f"Unknown error while retrieving file '{filepath}' for shot {shotID}.")

    return {
        "status": "success",
        "shot_id": shotID,
        "file_path": filepath,
        "file_content": data
    }

@SERVER.tool("getShotJSON", description="Get a JSON file from a shot. File path is relative to the shot's root directory. Field path is the value in the JSON file.Example: getShotJSON(0, 'conductor/discharge.json', 'parameters/infrastructure.toroidal_magnetic_field/voltage_v')")
def MCP_getShotJSON(shotID: int, JSONfilePath: str, JSONfieldPath: str):
    filepath = cleanseURL(JSONfilePath)
    shotID, err = _resolve_shot(shotID)
    if err:
        return err

    try:
        value = _read_json_field(shotID, filepath, JSONfieldPath)
    except Exception as e:
        return _json_field_error(e, shotID, filepath, JSONfieldPath)

    return {
        "status": "success",
        "shot_id": shotID,
        "file_path": filepath,
        "field_path": JSONfieldPath,
        "value": value
    }

@SERVER.tool("listJSONchildFields", description="Shallowly list the child fields of a JSON field in a file. File path is relative to the shot's root directory. Example: listJSONchildFields(0, 'conductor/discharge.json', 'quantities/diagnostics.basic_diagnostics/discharge')")
def MCP_listJSONchildFields(shotID: int, JSONfilePath: str, JSONfieldPath: str):
    filepath = cleanseURL(JSONfilePath)
    shotID, err = _resolve_shot(shotID)
    if err:
        return err

    try:
        value = _read_json_field(shotID, filepath, JSONfieldPath)
    except Exception as e:
        return _json_field_error(e, shotID, filepath, JSONfieldPath)

    if isinstance(value, dict):
        child_fields = list(value.keys())
    elif isinstance(value, list):
        child_fields = [str(i) for i in range(len(value))]
    else:
        child_fields = []

    return {
        "status": "success",
        "shot_id": shotID,
        "file_path": filepath,
        "field_path": JSONfieldPath,
        "child_fields": child_fields
    }

@SERVER.tool("listDirectory", description="List files and directories in a directory. File path is relative to the shot's root directory. Example: listDirectory(0, 'Diagnostics/BasicDiagnostics')")
def MCP_listDirectory(shotID: int, directory: str = ""):
    directory = cleanseURL(directory)
    shotID, err = _parse_shot_id(shotID)
    if err:
        return err

    try:
        entries = GOLEMC.listDirectory(shotID, directory)
    except FileNotFoundError:
        return _error("DIRECTORY_NOT_FOUND", f"Directory '{directory}' not found for shot {shotID}.")
    except Exception:
        return _error("UNKNOWN_ERROR", f"Unknown error while listing directory '{directory}' for shot {shotID}.")

    return {
        "status": "success",
        "shot_id": shotID,
        "directory": directory,
        "entries": entries
    }

@SERVER.tool("awaitShot", description="Wait for a shot to be triggered. Returns when the shot exists or after a timeout.")
async def await_shot(shotID: int) -> str:
    shotID, err = _parse_shot_id(shotID)
    if err:
        return err

    deadline = time.monotonic() + AWAIT_TIMEOUT
    while time.monotonic() < deadline:
        # The probe is blocking I/O, so run it off the event loop.
        if await asyncio.to_thread(_shot_exists, shotID):
            return f"Shot '{shotID}' exists."
        await asyncio.sleep(AWAIT_POLL_INTERVAL)

    return f"Waiting for shot '{shotID}' timed out ({AWAIT_TIMEOUT}s)."
#endregion

#region GOLEM know-how
@SERVER.resource("guide://basics", name="How to serve as a GOLEM discharge assistant", description="Basic guide for serving as a discharge assistant")
def guide_basics():
    return _read_knowledge(KNOWLEDGE_BASICS)

@SERVER.resource("guide://status", name="Things to know before proposing shots", description="Everything temporary to take into account before proposing shots")
def guide_status():
    return _read_knowledge(KNOWLEDGE_STATUS)
#endregion

#region RUNTIME
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    SERVER.run()  # stdio
#endregion
