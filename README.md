# GOLEM AI Discharge assistant workflow
> [!NOTE]
> This is a work in progress, yet to be properly tested (on GOLEM!).

Link an [MCP](https://modelcontextprotocol.io/docs/2026-07-28/getting-started/intro)-capable [LLM](https://en.wikipedia.org/wiki/Large_language_model) to let it propose configurations on the [GOLEM](https://golem.fjfi.cvut.cz/) tokamak. \
The MCP server provides AI with an intuitive way to view the latest shot data ([shot database](http://golem.fjfi.cvut.cz/shots/0/) via HTTP or filesystem) and lets it propose a [Discharge command]
(http://golem.fjfi.cvut.cz/shots/0/Operation/Discharge/Styles/index.html) which will (after the operator accepts it) be performed on the tokamak. \
This is an interative process and will adapt shots to the operator's needs (whether plasma stability or best [MHD](https://en.wikipedia.org/wiki/Magnetohydrodynamics) anomaly detection, depends on instructions) to a point where GOLEM personnel can resume under better conditions without spending time on finding them.

## Setup
1. Clone the repository: `git clone https://github.com/LeosPetzold/golemLLM`
2. Create a Python virtual environment in the `golemLLM` repo directory: `python3 -m venv .venv`
3. Activate the virtual environment: `source .venv/bin/activate`
4. Install required packages: `pip install -r requirements.txt`
5. Add `server.py` as MCP server
6. Roll
The following can be used for configuring `mcp.json` for Visual Studio Code:
```json
{
  "servers": {
    "GolemLLM": {
      "type": "stdio",
      "command": "${workspaceFolder}/.venv/bin/python",
      "args": ["-m", "golemLLM.server"],
      "env": {
        "PYTHONPATH": "${workspaceFolder}/src"
      }
    }
  }
}
```

---
[A wonderful image brought to you by GOLEM _static](http://golem.fjfi.cvut.cz/_static/nuclear.png) (yes, I know how to do images)
