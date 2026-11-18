# Reading GOLEM shots: signals, quantities and how to analyse them

Use this guide when you analyse a shot. Save `conductor/discharge.json` to your workspace first, then process it with a script. Do not load the raw file into context.

## 1. Workflow for each shot

1. Get the shot ID from `shot_no` (or `GM#` the operator gives you). Check `outcome` and `plan/execution_ready` first. A refused or failed preparation has no plasma data.
2. Read `number`, `session_number`, `shift_number`, `comment`, and `plan/setup_document/id` to place the shot in context.
3. Read `parameters/` to know what was asked for.
4. Read `quantities/` for what was measured. For each value, read its `description` and `unit` once; the descriptions say what the value actually is (for example a 0.99 quantile, not a maximum).
5. Read `evidence` only when a phase failed or a value is missing.
6. Compare with the reference shot (`basics.md`) and the last 2 to 5 shots of the same series.

Use `getShotJSON` and `listJSONchildFields` to explore field names before downloading. Use `getShotFile` for the whole file only once.

## 2. Headline quantities (basic diagnostics)

- `loop_voltage_high` (q99) and `loop_voltage_median`: the drive during the plasma interval. The median is the 0.5 quantile, not a mean. High q99 with low median can mean a breakdown spike.
- `plasma_current_high` (q99) and `plasma_current_median` (kA): plasma current over the plasma interval. Median is the stable plateau; q99 is the peak.
- `chamber_current_median` and `_high` (kA): chamber current solved from the chamber's L/R equation against loop voltage; not measured directly.
- `toroidal_field_median` and `_high` (T): Bt over the plasma interval, integrated from the pick-up coil and calibrated by K_BtCoil.
- `discharge_trigger`: the trigger channel itself. Use it as the time zero for all other signals.
- `photodiode_voltage`: visible light; rises at breakdown and falls at a disruption.
- `diamagnetic_voltage`: diamagnetic loop; related to plasma pressure. Interpret with care, it is a small signal.

Plasma interval: the notebook defines the plasma interval from the data. If the interval is empty or very short, the headline quantities are not meaningful. Report that instead of a value.

## 3. Interferometry

- `line_averaged_density_high` and `_mean` ($\text{m}^{-3}$): line-averaged electron density over the plasma interval.
- Compare with the Greenwald estimate in `guide://tokamak-primer` (computed from the current Ip and geometry, see `guide://tokamak-primer`). Densities approaching or above the estimate correlate with disruption.
- A density that grows while plasma current falls is a warning sign of edge cooling and wall outgassing.

## 4. Pressure and gas

- `infrastructure.working_gas/discharge/pressure_predischarge_mpa`: pressure measured just before firing. The most useful gas value.
- `pressure_before_mpa` vs `pressure_after_mpa`: how much the shot changed the chamber. A large rise is outgassing or a disruption.
- `difference_mpa` vs the tolerance: whether the shot was in range.

## 5. Capacitor banks and charging

- `peak_bank_voltage_v`, `duration_s`, `final_source_current_a`: how the banks behaved. A bank that does not reach its target points to a charging problem, not a plasma problem.
- `source_v` and `source_a` are shared between banks; do not attribute them to one bank.

## 6. Stabilisation

- Waveform set points come from `parameters/` (`infrastructure.position_stabilization`, `infrastructure.current_stabilization`). Compare with the waveform shape the operator uses (see the LIMITS section of `guide://basics`).
- Saturation: the set point asks for more than the generator or supply can give. This shows up as a flat top in the measured signal and as lost control later in the shot.

## 7. Repeatability and noise

- Plasma is often chaotic. Judge a change by a series, not one shot: 3 to 5 shots with the same setup, looking at the spread of `plasma_current_median`, `loop_voltage_high`, and duration.
- Report the spread with the value. a median with its range over the series is useful; a single median alone is not.
- A single outlier shot is a reason to look at the evidence, not a reason to change parameters.

## 8. Missing data

- A missing file or empty field usually means a diagnostic did not run or a parameter was not supplied (`basics.md`). Check `plan/modules` roles for `bound: false` or `status` not executable before assuming a physics cause.
- Missing diagnostics are not zero. Say "not recorded" and do not compute a value from a missing signal.

## 9. Writing the analysis

For each shot, state: the setup change (if any), the headline values with their spread, one observation about the plasma, and whether it supports the current hypothesis. Keep it to a few lines. Attach the script you used so the operator can rerun it.
