# Experiment design on GOLEM: planning a series of shots

A single shot tells you little. A plan tells the operator what each shot is for, what result would confirm or reject a hypothesis, and when to stop. Use this guide before proposing a series.

## 1. Start from a question

Write the question in one sentence before choosing parameters. Examples:
- Does a higher fill pressure raise the breakdown reliability at fixed Bt?
- Does a later current stabilisation ramp lengthen the plasma interval?
- Does helium conditioning change the repeatability of the plasma current plateau?

If the question cannot be answered by the signals in `guide://reading-shots`, change the question or ask the operator for a diagnostic.

## 2. Pick one variable at a time

- Change one parameter per series, or one parameter per block of shots. Hold everything else at the reference shot's values.
- Record the setup difference explicitly in each proposal (the reasoning line of the proposal).
- Avoid changing gas, conditioning and waveforms in the same step. You will not know which one mattered.

## 3. Use a reference and a scan

- Reference shot: a real GM# shot with good repeatability, chosen by the operator. All proposals in a series refer to it.
- Scan: 3 to 5 values of the chosen variable, spanning the range the reference suggests is safe. Start in the middle, move outward only if the shots are clean.
- Repeat the best point 2 to 3 times before claiming a trend.

## 4. Decide what counts as success

Before the first shot, state:
- The quantity that will be compared (for example `plasma_current_median` and its spread).
- The change you consider meaningful. Ten per cent of a noisy quantity is probably noise; check against the spread of the reference series.
- What would reject the hypothesis.

Write these down in the plan. Do not move the goalposts after seeing the data.

## 5. Stopping rules

Stop the series and report when any of these holds:
- Two consecutive refusals or failures in the same phase (see `guide://failure-modes`).
- Any safety-related signal (see `guide://failure-modes`, section 3).
- The scan has shown a clear result, or the spread is larger than the effect.
- The operator asks to stop, or the session or shift ends (`guide://session-control`).

## 6. Between shots

- Compare each new shot with the reference and the previous shot; write one line of observation.
- Decide the next step from the data, not from a plan you wrote earlier. Say what changed your mind.
- If the wall state or pressure has drifted, propose conditioning before the next scan point (`guide://wall-conditioning`).

## 7. Reporting a series

At the end of a series, report:
- The question, the variable, and the values scanned.
- The reference shot and the shots in the series (GM# list).
- The headline values with their spread (not single numbers).
- What the result supports and what it does not. Name the uncertainty.
- The next question, if there is one.

## 8. Ground rules for proposals

- One proposal per message, at the end (`guide://basics`).
- Each proposal has a title, reasoning, reference shot and command (`guide://basics`).
- Do not propose a new scan point in the same message as a change in conditioning or gas. Keep them in separate blocks, and let the operator approve each.
- Keep a running list of what has been tried in the session, so you do not repeat a point without a reason.
