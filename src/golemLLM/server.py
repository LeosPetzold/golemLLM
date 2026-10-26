# MCP server, main

from mcp.server.mcpserver import MCPServer
from mcp.server.apps import Apps
from mcp.types import Resource
from pathlib import Path
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

KNOWLEDGE_BASICS = os.path.join(os.path.dirname(__file__), "MCP", "basics.md")

DRY_RUN = True  # Testing purposes only, prevents from running discharges
TTL = 3600  # Time a proposal is valid for [s]
UI_URI = "ui://proposal.html"
UI_FILE = Path(__file__).parent / "ui" / "proposal.html"

LOGGER = logging.getLogger("MCPGolemLLM")
SERVER = MCPServer("GolemLLM", title="GOLEM AI discharge assistance toolkit", instructions=INSTRUCTIONS)
GOLEMC = (GolemCLIENTlocal(CLIENT_LOCAL_SHOTSDIR, cache=CACHE_FILES, verbose=VERBOSE)
          if LOCAL else GolemCLIENThttp(CLIENT_HTTP_SHOTSURL, cache=CACHE_FILES, verbose=VERBOSE))

#region GOLEM data access
existence_cache = {} # Shot existence checks cache
@SERVER.tool("getShotFile", description="Get a file from a shot. File path is relative to the shot's root directory. Example: getShotFile(0, 'Production/Parameters/FullCommandLine')")
def MCP_getShotFile(shotID: int, filePath: str):
    filePath = filePath.replace(".", "")

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

@SERVER.tool("listDirectory", description="List files and directories in a directory. File path is relative to the shot's root directory. Example: listDirectory(0, 'Production/Parameters')")
def MCP_listDirectory(shotID: int, directory: str = ""):
    directory = directory.replace(".", "")

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
            "message": f"Unknown error while listing directory '{directory}' for shot {shotID}. {e}"
        }
    except FileNotFoundError:
        return {
            "status": "error",
            "error_type": "FILE_NOT_FOUND",
            "message": f"Directory '{directory}' not found for shot {shotID}."
        }
    except Exception as e:
        return {
            "status": "error",
            "error_type": "UNKNOWN_ERROR",
            "message": f"Unknown error while retrieving directory '{directory}' for shot {shotID}."
        }


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
#endregion

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    SERVER.run()  # stdio