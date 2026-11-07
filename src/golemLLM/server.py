# MCP server, main

import asyncio
import time

from mcp.server.mcpserver import MCPServer
from pathlib import Path
from urllib.parse import urlparse, unquote
import json
import logging
import os

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
QUEUE_FILE = Path(os.environ.get("GOLEMLLM_QUEUE", Path(__file__).resolve().parents[2] / ".golemllm" / "proposals.jsonl"))

LOGGER = logging.getLogger("MCPGolemLLM")
GOLEMC = (GolemCLIENTlocal(CLIENT_LOCAL_SHOTSDIR, cache=CACHE_FILES, verbose=VERBOSE)
          if LOCAL else GolemCLIENThttp(CLIENT_HTTP_SHOTSURL, cache=CACHE_FILES, verbose=VERBOSE))

SERVER = MCPServer("GolemLLM", title="GOLEM AI discharge assistance toolkit", instructions=INSTRUCTIONS)

#region Proposals
@SERVER.tool("proposeDischarge", description="Propose a discharge to the operator.")
def MCP_proposeDischarge(proposalTitle: str, proposalReason: str, referenceShotID: int, proposedCommand: str):
    try:
        referenceShotID = int(referenceShotID)
        if referenceShotID < 0:
            raise ValueError
    except (ValueError, TypeError):
        return {
            "status": "error",
            "error_type": "INVALID_SHOT_ID",
            "message": f"Invalid referenceShotID '{referenceShotID}'. Must be a non-zero integer."
        }

    QUEUE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(QUEUE_FILE, "a") as f:
        f.write(json.dumps({
            "time": time.time(),
            "title": proposalTitle,
            "reason": proposalReason,
            "reference_shot_ID": referenceShotID,
            "proposed_command": proposedCommand,
        }) + "\n")
    with open(QUEUE_FILE) as f:
        index = sum(1 for _ in f)

    return (
        f"GsP#{index} queued: decide it in the GolemLLM proposals pane (not sent to Conductor).\n"
        f"+------------------------------------------------------------\n"
        f"| {proposalTitle}\n"
        f"| Reference shot: GM#{referenceShotID}\n"
        f"| Reasoning: {proposalReason}\n"
        f"| Command: {proposedCommand}\n"
        f"+------------------------------------------------------------"
    )
#endregion

#region GOLEM data access
existence_cache = {} # Shot existence checks cache
@SERVER.tool("getShotFile", description="Get a file from a shot. File path is relative to the shot's root directory. Example: getShotFile(0, 'conductor/discharge.json')")
def MCP_getShotFile(shotID: int, filePath: str):
    filepath = cleanseURL(filePath)

    try:
        shotID = int(shotID)
    except (ValueError, TypeError):
        return {
            "status": "error",
            "error_type": "INVALID_SHOT_ID",
            "message": f"Invalid shotID '{shotID}'. Must be an integer."
        }
    
    if shotID != 0:
        if shotID not in existence_cache:
            existence_cache[shotID] = GOLEMC.shotProbeHEAD(shotID)
        if not existence_cache[shotID]:
            return {
                "status": "error",
                "error_type": "SHOT_NOT_FOUND",
                "message": f"Shot {shotID} not found."
            }
    try:
        data = GOLEMC.getShotFileCached(shotID, filePath)
        return {
            "status": "success",
            "shot_id": shotID,
            "file_path": filePath,
            "file_content": data
        }
    except FileNotFoundError:
        return {
            "status": "error",
            "error_type": "FILE_NOT_FOUND",
            "message": f"File '{filePath}' not found for shot {shotID}."
        }
    except Exception as e:
        return {
            "status": "error",
            "error_type": "UNKNOWN_ERROR",
            "message": f"Unknown error while retrieving file '{filePath}' for shot {shotID}."
        }

@SERVER.tool("listDirectory", description="List files and directories in a directory. File path is relative to the shot's root directory. Example: listDirectory(0, 'Diagnostics/BasicDiagnostics')")
def MCP_listDirectory(shotID: int, directory: str = ""):
    directory = cleanseURL(directory)

    try:
        shotID = int(shotID)
    except (ValueError, TypeError):
        return {
            "status": "error",
            "error_type": "INVALID_SHOT_ID",
            "message": f"Invalid shotID '{shotID}'. Must be an integer."
        }

    try:
        data = GOLEMC.listDirectory(shotID, directory)
        return {
            "status": "success",
            "shot_id": shotID,
            "directory": directory,
            "entries": data
        }
    except FileNotFoundError:
        return {
            "status": "error",
            "error_type": "DIRECTORY_NOT_FOUND",
            "message": f"Directory '{directory}' not found for shot {shotID}."
        }
    except Exception as e:
        return {
            "status": "error",
            "error_type": "UNKNOWN_ERROR",
            "message": f"Unknown error while listing directory '{directory}' for shot {shotID}."
        }

@SERVER.tool("awaitShot", description="Wait for a shot to be triggered. Returns when the shot exists or after a timeout.")
async def await_shot(shotID: int) -> str:
    start_time = time.time()

    try:
        shotID = int(shotID)
    except (ValueError, TypeError):
        return {
            "status": "error",
            "error_type": "INVALID_SHOT_ID",
            "message": f"Invalid shotID '{shotID}'. Must be an integer."
        }
    
    while time.time() - start_time < 3600:
        is_triggered = GOLEMC.shotProbeHEAD(shotID)
        
        if is_triggered:
            return f"Shot '{shotID}' exists."
            
        await asyncio.sleep(2)
        
    return f"Waiting for shot '{shotID}' timed out ({3600}s)."
#endregion

#region GOLEM know-how
@SERVER.resource("guide://basics", name="How to serve as a GOLEM discharge assistant", description="Basic guide for serving as a discharge assistant")
def guide_basics():
    try:
        with open(KNOWLEDGE_BASICS, "r") as f:
            return f.read()
    except FileNotFoundError:
        return {
            "status": "error",
            "error_type": "FILE_NOT_FOUND",
            "message": f"Knowledge file not found."
        }
@SERVER.resource("guide://status", name="Things to know before proposing shots", description="Everything temporary to take into account before proposing shots")
def guide_basics():
    try:
        with open(KNOWLEDGE_STATUS, "r") as f:
            return f.read()
    except FileNotFoundError:
        return {
            "status": "error",
            "error_type": "FILE_NOT_FOUND",
            "message": f"Knowledge file not found."
        }
#endregion

#region Helpers
def cleanseURL(url: str) -> str:
    return urlparse(unquote(url)).path.replace("..", "") # non-func
#endregion

#region RUNTIME
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    SERVER.run()  # stdio
#endregion