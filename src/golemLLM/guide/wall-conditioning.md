# Wall conditioning on GOLEM (chamber conditioning)

Wall conditioning cleans the vessel wall between shot series, so that impurities from air and previous plasmas do not dominate the next discharges. It is a **non-discharge operation**. You plan and check it; the operator performs every physical step.

Read `guide://conductor` first for the role and limits.

## 1. Methods

Three conditioning methods appear in the legacy record (`Operation/Session/Conditioning.sh`):

- **Baking**: heating the chamber with the baking relay on (relay 1). Starts with the Et commutator off (`EtCommutatorOFF` on the charger) and then baking on. Logged as `baking:start` / `baking:end` in the chamber log.
- **Glow discharge (GDC)** in working gas: a low-pressure glow across the chamber, with the glow supply on relay 11 and a gas flow set on the Instek supply. Logged as `glow discharge:init`, `glow discharge:start`, `glow discharge:end`.
- **Pumping** between operations: rotary and turbo pumps and vent valves. Logged as `pumping:start` / `pumping:end`. Pumping is part of the session, see `guide://session-control`.

Legacy GDC procedure, in order:
1. Initialise: glow supply on, turbo pumps on standby, vent 1 closed, helium (He) gas valve open. Operator then engages the HV supply and the gas reservoir.
2. Start: operator sets the gas flow and the supply to its working point (legacy: the values are set by the operator from the legacy procedure, flow set by `GlowDischGasFlowSetup`), and the glow runs for a timed interval (legacy: checked in regular steps).
3. Stop: supply output off, wait, glow supply off, turbo standby off, vent 1 open, He valve closed, reservoir closed.

The timed interval and the supply values are legacy defaults. They are not confirmed for Conductor. Use them as the starting point for a plan, and say so.

## 2. What you need to know before proposing conditioning

Check these from the most recent shots and from the operator:

- **Chamber pressure** (mPa) and **chamber temperature** (°C) at the start of the step, and the pressure at the end. A glow that does not change pressure, or a pressure that does not settle, is a fault to report.
- **Forevacuum pressure** (Pa) before pumping is started. A rough-pump problem blocks everything downstream.
- **Gas state**: which gas is in the chamber now and which gas is next (see `infrastructure.working_gas`, `gas` and `pressure_mpa`). Changing gas without pumping out the previous one contaminates the next shots.
- **Time since last conditioning** and what the last shots looked like. If the plasma got noisier, conditioning is usually the first proposal, not another discharge parameter change.
- **Operator availability**: GDC requires a person at the HV supply and the gas reservoir. Do not propose it when nobody is present.

## 3. How to propose a conditioning step

Non-discharge steps are not sent through `proposeDischarge`. Write them in chat as a checklist, indexed as a **GsP** plan item only if the operator asks for a numbering scheme. Each item must contain:

1. The operation and its purpose, in one sentence.
2. Preconditions the operator checks first (pressure, temperature, gas, people present, nothing running).
3. The steps, one per line, in order, with the physical action (for example "open He reservoir", "set supply to the value from the procedure").
4. The expected reading after each step (for example "chamber pressure rises within the expected time", "forevacuum below the value you saw last time").
5. The stop condition and what to do if it is not met. The default is to stop and report, not to continue.
6. What you want to see afterwards: which quantity, from which shot or log, to check the result.

Ask the operator to confirm each block before moving on. Do not chain a conditioning step and a discharge in one message.

## 4. Logging

Every conditioning step writes a row to `chamber_management` (event, date, time, shot number, session ID, chamber pressure, forevacuum pressure, chamber temperature). The shot number and session ID at the time of the event are what you need to link a conditioning step to the shots after it. Ask the operator for the relevant log rows when you need them. You do not have direct database access.

## 5. Evaluating the effect

After conditioning, compare the first 3 to 5 shots with the shots before it:
- Plasma duration, loop voltage, and the stability of the plasma current (`quantities/diagnostics.basic_diagnostics/discharge/*`).
- Line-averaged density (`quantities/diagnostics.interferometry`) for signs of wall outgassing.
- Pressure before discharge (`infrastructure.working_gas/discharge/pressure_predischarge_mpa`) for drift.

Say what changed and how many shots you have. Three shots is not a trend. Do not claim conditioning worked from one good shot.

## 6. Known gaps

- No Conductor module for conditioning is present in the material this server reads. The procedures here are the legacy ones.
- Legacy values (relay numbers, supply voltages and currents, GDC interval, pressure examples) are reference only.
- Check with the operator before any change to the relay or supply mapping. The mapping is hardware-specific.
