# Tokamak primer: how the machine works as a system

Read this before any other operator guide. It explains the physics and the subsystems in the order a discharge uses them. Numbers for GOLEM are in `guide://golem-systems`. Shot analysis is in `guide://reading-shots`.

## 1. The idea

A tokamak confines a hot plasma (ionised gas) in a torus with magnetic fields. Three fields matter:

- **Toroidal field Bt**: runs around the torus, produced by external coils. It sets the confinement scale. It is the strongest field and it is set by the Bt capacitor bank before the shot.
- **Plasma current Ip**: runs around the torus through the plasma. It produces the poloidal field Bp that twists the field lines into helices. The combination of Bt and Bp confines the plasma.
- **Poloidal/vertical and radial fields**: produced by control coils. They hold the plasma column in place (position), since a plasma is not stable on its own.

The plasma is the secondary of a transformer. The central iron core of GOLEM is the primary, and changing the flux in the core drives a toroidal electric field that drives Ip. That is the "transformer" in the usual description of Ohmic tokamaks.

## 2. Breakdown and start-up

Before any current flows, the gas must be ionised. This is breakdown.

- The toroidal electric field E (from the loop voltage $V_\text{loop} = 2\pi R\,E$) accelerates free electrons. Ionising collisions create a plasma avalanche.
- Breakdown needs enough field and the right fill pressure. Too high a pressure stops avalanching (collisions scatter electrons too often). Too low a pressure lets electrons run away to high energy and form runaway beams.
- A simple scaling is Paschen's law: breakdown voltage depends on the product $p\,d$ of pressure and gap length, with a minimum at a particular pressure. In a tokamak the gap is the torus circumference $2\pi R$, so the loop voltage plays the role of the voltage. Practical tokamaks sit near the Paschen minimum. The simple Townsend model does not fully describe breakdown in a toroidal field, so treat Paschen as a starting point for choosing a fill pressure, not as a design rule.
- Signature of breakdown in data: a jump in loop voltage (`loop_voltage`) followed by a rise in plasma current and light (photodiode). Breakdown is usually the largest loop-voltage spike of the shot.

## 3. Ohmic heating and current

- Ohmic heating power is $P = V_\text{loop}\, I_p$ (minus an inductive term during changes of current). The plasma heats itself through its own resistance.
- $I_p$ rises while $V_\text{loop}$ is positive. The loop voltage is the drive; $I_p$ is the response. $I_p$ falls when the loop voltage drops or reverses.
- Plasma resistance falls as temperature rises (roughly as $T_e^{-3/2}$), so a well-heated plasma needs a smaller loop voltage to carry the same current. This is why the current often rises fast early and then flattens.
- Ip can only be driven as long as the transformer flux lasts. The discharge duration (see the current pulse-length limit in `guide://golem-systems`) is set by the energy stored in the core and the coils, not by the operator alone.

## 4. Safety factor q and the density limit

- The safety factor q (roughly, how many times a field line goes around the torus for each time it goes around the plasma poloidally) sets stability. A common estimate at the edge is $q_a \approx \dfrac{2\pi a^2 B_t}{\mu_0 R I_p}$. Low q (below about 2) tends to be unstable (disruptive); high q is more stable.
- Insert the current GOLEM values of R, a, Bt and Ip into this formula to estimate q_a. Use the operator's current values. The estimate is from the formula, not a measurement. Check the value with the operator's own definition before relying on it.
- The Greenwald density limit is an empirical cap on line-averaged density: $n_G \approx \dfrac{I_p}{\pi a^2}$, with $I_p$ in MA, $a$ in m, giving $n_G$ in units of $10^{20}\,\text{m}^{-3}$. For GOLEM, insert the current Ip and a into this formula to get the limit for the operating point. Going above it usually leads to edge cooling, radiative collapse and disruption. Density above the limit is a warning, not a target.

## 5. Disruptions

A disruption is a sudden loss of the plasma's confinement and current. Typical signs:
- Sudden drop in plasma current and in photodiode light.
- Spike in loop voltage (often negative) at the moment of the loss.
- Growing MHD activity (magnetic fluctuations, Mirnov coils) just before.
- Loss of vertical position, if the position control cannot keep up.

Disruptions are the main way a small tokamak loses shots. Causes include density approaching the limit, low q, impurities, a poorly controlled plasma position, and a wall that is not conditioned. A disruption is information: check which of the above preceded it before changing anything.

## 6. Position control

- An elongated plasma is vertically unstable without control. A vertical field, produced by feedback coils, holds it in place. The vertical growth time sets how fast the control must respond.
- A radial field moves the plasma column across the chamber. It is used to centre the plasma and to keep it off the limiter.
- Control coils need power supplies with limited voltage, current and rate. Saturation (a waveform asking for more than the supply can give) means the plasma is not controlled in that phase.
- The vertical field needs to change as Ip and the plasma shape change during the shot (it is a time-dependent set point, not a fixed value). Stabilisation waveforms in the Conductor parameters are these set points.

## 7. Impurities and the wall

- The plasma interacts with the vessel wall. Particles released from the wall (oxygen, water, carbon, hydrogen stored in the walls) dilute the plasma and radiate energy.
- Radiation from impurities cools the plasma edge and can drive density-limit disruptions. Clean walls give better, more repeatable shots.
- Conditioning (baking, glow discharge, helium cleaning) is the main way of reducing wall impurities between shot series. See `guide://wall-conditioning`.

## 8. Why shots are not repeatable by default

Each shot starts from a different wall state, a different gas residue, a different charge in the capacitor banks and a different plasma start. Repeatability is achieved by:
- Stable conditioning and pressure before each shot.
- The same setup parameters on each shot in a series.
- Enough shots to separate a real effect from noise (plasma is often chaotic).

## Sources (general physics; verify against the primary references before using numbers)

- Greenwald density limit, density-limit disruptions and MHD activity: arXiv paper on density limit and disruptions, https://www.arxiv.org/pdf/2601.15590 ; FT tokamak study on disruptions and density, https://sostenibilita.enea.it/pubs/5746
- Ohmic heating power relation ($V_\text{loop} I_p$ with an inductive term): IR-T1 paper, https://www.redalyc.org/pdf/464/46436211.pdf
- Breakdown, Paschen analogy and fill-pressure window: Journal of Plasma Physics 2018, "On the breakdown modes and parameter space of Ohmic tokamak start-up", https://ui.adsabs.harvard.edu/abs/10.1017/S0022377818001046 ; PPPL-4836, https://bp-pub.pppl.gov/pub_report/2013/PPPL-4836.pdf
- Vertical stabilisation and feedback coils: TES paper, https://arxiv.org/pdf/1503.03135 ; De Tommasi et al., https://link.springer.com/content/pdf/10.1007/s10894-018-0162-5.pdf
- Vertical field readjustment during ramp: Alcator C notes, cited in the search above; EXL-50U control paper, https://arxiv.org/pdf/2608.20901
