# golemllm-proposals

A Claude Code mod (a pane beside the chat) that lists GolemLLM discharge proposals and records the operator's approve or deny decision.

## What it shows
- Each proposal from `.golemllm/proposals.jsonl` as one row, numbered `GsP#n`.
- **Pending** rows are open: reference shot, reasoning, command, and Approve / Deny buttons.
- **Decided** rows are folded and coloured soft green (approved) or soft red (denied). Press a row to open or fold it.
- The list refreshes every 2 seconds, so new proposals appear without a restart.
- The pane scrolls with the touchpad or wheel. Scroll indicators (`▲ more above`, `▼ more below`) appear inside the scrolling content, so they only show near the edges.

## What it does not do
- Approve and Deny write one line to `.golemllm/decisions.jsonl`. **Nothing is sent to Conductor or the tokamak.**
- A proposal can be decided once; a second press is ignored.
- Paths are relative to the session's working directory, so start Claude Code from the repo root.

## Setup
1. Load the mod from the repo: `claude --plugin-dir mods/golemllm-proposals`, started from the repo root.
2. Start a session; the pane opens at start. If Claude Code asks whether to turn on mods written in this session, answer "Turn them on".
3. The queue comes from the GolemLLM MCP server (`proposeDischarge` in `src/golemLLM/server.py`), which appends to the same file.

## Data files
| File | Written by | Contents |
| --- | --- | --- |
| `.golemllm/proposals.jsonl` | MCP server | one proposal per line: `time`, `title`, `reason`, `reference_shot_ID`, `proposed_command` |
| `.golemllm/decisions.jsonl` | this mod | one decision per line: `index`, `decision`, `time`, `proposal` |

## Known limits
- The bottom scroll indicator is estimated from the content height, so it can be off by a row or two.
- Nothing is verified against live hardware.
- The shot client reads the GOLEM shot server over HTTP; it keeps its cache in memory and writes nothing to disk.

## Layout
- `.claude-plugin/plugin.json` — manifest
- `hooks/hooks.json`, `hooks/register.tsx` — the module
- `types/index.d.ts` — state contract for the pane's values
