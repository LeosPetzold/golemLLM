# Session and shift control on GOLEM

A **session** is a block of shots run with one mission (for example a probe scan or a stability series). A **shift** is the working period of a team within a session. Both have their own numbering and their own logbook. This guide covers how you read them, how you plan changes to them, and what you propose versus what the operator does.

Read `guide://conductor` first for the role and limits.

## 1. What identifies a session and a shift

From a Conductor record (`conductor/discharge.json`):
- `session_number`: the session the shot belongs to.
- `shift_number`: the shift the shot belongs to.
- `plan/setup_document/id` and `name`: the session setup. The setup defines the modules, the safety profile and the limits for the whole session. A different setup means a different session, even if the number is the same.
- `requires_shift_modules`: modules that must be ready before a shift starts (currently `infrastructure.chamber`).

From the legacy shot root directory: `session_id` (the first shot ID of the session), `comment` and `shot_no`. `session_id` is useful for data mining across a session.

Shot numbers, session numbers and shift numbers are **different counters**. Do not write one where another is meant. In chat, refer to shots as `GM#xxxxx`, and say the session or shift number in full.

## 2. Session lifecycle (legacy)

Legacy `Dirigent.sh` and `Operation/Session/Operator.sh`:

1. **Setup**: the session setup file is loaded and copied to the shared session directory. The environment is prepared on every device (`PrepareSessionEnv`).
2. **Open** (`-o`/`--open_session`, or `os` for broadcast open): the session ID is set to the last shot number plus one, the session date and mission are written, the session row is inserted into the database, and a snapshot of the control directory is zipped.
3. **Operate**: shots run inside the session. Operator reminders are printed at opening: open gas valves at the start of every session, run the long-term stability test, and do a working-gas calibration when needed.
4. **Close** (`-c`/`--close_session`): the end shot number, end time and end chamber pressure are recorded, the session directory is archived, and the session's helpers are stopped.

Each step prints a broadcast line in the log. Read those lines when a session misbehaves.

## 3. Shift handover

Shifts are not opened and closed by a separate shell command in the legacy material. A shift change in Conductor is expected to go through the `infrastructure.chamber` module and the session workflow. The exact handover steps are **not documented** in any file this server reads. For a shift handover:

- Ask the operator for the handover note. You can help write it from the shot data.
- The note should include: the last shot and its outcome, the chamber pressure and temperature, the gas and pressure set, any open conditioning step, any fault or refusal, and the next planned proposal.
- Do not treat a shift change as a reset. The plasma state carries over.

## 4. What you can propose

Session-level changes are proposed in chat, never executed by you. Typical proposals:

- **Open a session** for a new mission. State the mission in one line, the setup you assume, the reference shots to use and the first proposal.
- **Continue a session**: a short status (last shot, outcome, chamber state, what is planned next). No proposal needed unless you have one.
- **Close a session**: the last shots to keep, the logbook items to record, and the chamber state to leave.
- **Pause for conditioning or pumping**: see `guide://wall-conditioning` for the steps and checks.

For each proposal, give the operator the **precondition**, the **steps**, the **expected reading** after each step and the **stop condition** (the same format as conditioning, section 3 of `guide://wall-conditioning`).

## 5. Checks you run at session start

Before the first proposal in a session:
1. Read `guide://status` for temporary facts.
2. Read the latest shot's `session_number`, `shift_number` and `plan/setup_document/id`. Note any change from the previous session.
3. Read the latest shot's `outcome` and `quantities` headline values.
4. Check the working-gas pressure before the shot against its setpoint.
5. Ask the operator what the session mission is, if it is not clear from the setup name or from the shot comments.

## 6. Known gaps

- The Conductor shift handover and any session-open or session-close command are not documented in the material this server reads.
- `Operation/Session/Controlling.sh` lists operator buttons (`open`, `reset`, `rsync`, `os`, `shutdown`, `sleep`, `wake`, `ping`). These are legacy. Their Conductor equivalents are unknown.
- Do not propose `shutdown`, `reset` or `sleep` without an explicit request from the operator. They affect every device.
