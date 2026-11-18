# Failure modes: what goes wrong on GOLEM and what to do about it

Use this when a shot fails, a plasma disrupts, or a preparation is refused. Always identify which phase failed before proposing a fix. A fix proposed for the wrong phase wastes a shot and can hide the real cause.

## 1. Find the phase first

Conductor records phases: preparing, arming, charging, executing, outcome. The first failing phase is the cause to look at. Read `outcome` and the matching `evidence` entries.

- Preparing refused: a precondition is not met (bank voltage not near zero, pressure out of range, module not executable). Nothing was charged. Fix the precondition; do not change physics parameters.
- Arming mismatch: a set point was written but read back differently (`voltage_v`, `current_a`, `setpoint_confirmed_mpa`). Check the device, not the plasma.
- Charging problem: a bank does not reach `target_voltage_v` (`peak_bank_voltage_v`), or the shared source is limited (`final_source_current_a`). Check the charging module and the source. Do not raise the target to compensate.
- Executing: trigger timing, breakdown, plasma phase and disruption. This is where physics analysis applies.

## 2. Common failures and their signatures

**No breakdown.** Loop voltage shows no spike, no current rise, no light. Check in order: Ecd bank read-back and `connect_primary`, fill pressure (`pressure_predischarge_mpa`) against the request, trigger timing (`discharge_trigger` vs the ECD and Bt lines), wall state (a dirty wall can absorb the breakdown). Suggest a conditioning step before changing gas pressure if the wall has been unconditioned for a while.

**Breakdown but short plasma.** Current rises, then falls within a few milliseconds. Check the loop voltage fall-off, density trend (`line_averaged_density`), and the photodiode decay. Typical causes: density too high for the current, poor position control, impurities. Density approaching the Greenwald estimate for the current Ip is a lead.

**Disruption.** Sudden loss of current and light, often with a loop voltage spike and MHD activity just before. Check the position control waveforms for saturation and the density trend. Do not raise Bt and Ip at the same time to fix a disruption; change one thing at a time.

**Position loss.** Vertical or radial position drifts before the disruption. Check the stabilisation waveform (ends in 0), its saturation, and the generator and scope readings. A waveform that saturates early is a set-point problem.

**Pressure refused.** Shot refused because `difference_mpa` exceeds `tolerance_mpa`. Check the regulator response and whether the gas supply is limiting. Do not widen the tolerance to make the shot run.

**Gas or pressure drift between shots.** Pressure before the shot keeps rising. Likely outgassing from the wall or a leak. Suggest pumping and conditioning, and log the trend. The operator decides on conditioning; you provide the reading and the plan.

**Wrong setup parameter.** A parameter was supplied in the wrong unit or with a wrong waveform format (for example a stabilisation waveform that does not end in 0). Check the command against the recent `Production/Parameters/CommandLine` pattern and the LIMITS in `guide://basics`.

**Missing diagnostic.** A diagnostic did not record. Check `plan/modules`, the diagnostic status, and whether the shot's comment mentions a known problem. Do not infer a physics result from a missing channel.

## 3. Safety-related responses

- Any refused gate that concerns voltage, pressure or interlocks: stop proposing discharges until the operator has checked the machine. Say so plainly.
- Any suspicion of hardware damage (unexpected bank behaviour, stabilisation saturation with no plasma, error messages from devices): report it to the operator immediately and propose no further shots.
- Never propose a workaround for a safety gate. A workaround is for the operator and the staff to decide.

## 4. How to write a failure report

- Shot: GM#xxxxx, session and shift number.
- Failed phase and the exact field showing it.
- Most likely cause, with confidence (low/medium/high) and why.
- Two checks the operator can do in the machine room or in the next shot's preparation.
- One proposal, if the cause is clear, or a request for information, if it is not.

## 5. What you cannot tell from data alone

Some causes need the machine and the operator: a leak, a loose connection, a gas valve sticking, a relay board reset. Say when a cause can only be checked physically. Do not present a hardware guess as a finding.
