# ⛔ PRELIMINARY GERBERS — DO NOT FABRICATE

These Gerbers/drill were auto-generated from the **routed-but-not-clean** 85×56 board
(2026-06-07). They are a **starting point for visualization only.**

**DRC at generation: 42 violations + 20 unrouted nets**, of which **22 are HV-net spacing
violations** in the high-voltage zone. The auto-router could only route the HV nets at ~2 mm
(below the 4 mm creepage required for 5 kV) — **the HV routing here is electrically UNSAFE.**

## Why it isn't fab-ready
The 2-channel **active-discharge** design (4 optos + 4 × 19 mm HV resistors + module + 2 terminals)
**does not physically fit** on 85×56 mm with 4 mm HV creepage. This was proven exhaustively (see
`docs/AUTONOMOUS_BUILD_LOG.md`). **Creepage is a 2-D surface constraint, so 4 layers does not help.**

## To get a clean, fabricable board
- **Enlarge to ~100×56 mm** (add ~15 mm on the HV/output side) — the HV zone then fits with full
  4 mm spacing and routes cleanly. (Overhangs the Pi USB-A end; clears with the ≥20 mm standoffs
  already required — see the Pi-IO note below.) **This is the recommended fix.**
- *or* drop active discharge (2 optos/channel) to fit 85×56.

## Mechanical (already accounted for in the design)
Use **≥20 mm M2.5 standoffs + a tall (≥20 mm) 2×20 GPIO stacking header** — the Pi 5's USB-A
(~17 mm) and RJ45 (~13.5 mm) sit under the right ~13 mm of this HAT (board x≈189.5–202). The B.Cu
GND pour shields the HV from the Pi's metal IO. (Marked on the `Dwgs.User` layer.)
