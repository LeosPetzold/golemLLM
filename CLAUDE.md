# GolemLLM

GOLEM tokamak discharge assistant. The MCP server in `src/golemLLM/server.py` serves shot data and operator guides.

- Claude Code connects through the project `.mcp.json` (server name `GolemLLM`). Use the `golem-discharge` skill for the proposal workflow in the terminal.
- The MCP app UI (`ui/proposal.html`) only renders in MCP Apps hosts. Claude Code receives the proposal as plain text.
- `DRY_RUN = True` in `server.py`. Do not change it without the operator's explicit instruction.
- Run the server locally with `.venv/bin/python -m golemLLM.server` and `PYTHONPATH=src`.
