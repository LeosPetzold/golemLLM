# MCP server, main

from mcp.server.mcpserver import MCPServer
from pathlib import Path
import logging

from golemLLM.core.client import GolemCLIENThttp, GolemCLIENTlocal

INSTRUCTIONS = """You are a research assistant aiding the operator in operating the GOLEM tokamak.
You may propose discharges inline with criteria of the operator's will, which may or may not be approved.
You may do so by sending a proposal to this MCP server.
Further instructions and experience in operating the tokamak may be found in KNOW_HOW.md (see MCP resources)."""

LOCAL = True  # Use local GolemClient for shots?
CACHE_FILES = True
CLIENT_LOCAL_SHOTSDIR = "/home/tG/shots/"
CLIENT_HTTP_SHOTSURL = "http://golem.fjfi.cvut.cz/shots"
VERBOSE = False  # Verbose logging for GolemClient

DRY_RUN = True  # Testing purposes only, prevents from running discharges
TTL = 3600  # Time a proposal is valid for [s]
UI_URI = "ui://proposal.html"
UI_FILE = Path(__file__).parent / "ui" / "proposal.html"


LOGGER = logging.getLogger("MCPGolemLLM")
SERVER = MCPServer("GolemLLM", title="GOLEM AI discharge assistance toolkit", instructions=INSTRUCTIONS)
GOLEMC = (GolemCLIENTlocal(CLIENT_LOCAL_SHOTSDIR, cache=CACHE_FILES, verbose=VERBOSE)
          if LOCAL else GolemCLIENThttp(CLIENT_HTTP_SHOTSURL, cache=CACHE_FILES, verbose=VERBOSE))

logging.basicConfig(level=logging.INFO)


