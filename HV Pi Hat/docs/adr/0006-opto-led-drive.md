# ADR-0006: Opto LED drive current

- Status: Accepted 2026-10-08 (Anatol: "go for your recommendations"). Pending bench test T1
  (`docs/BENCH_TESTS.md`).
- Deciders: Anatol Gogoj
- Supersedes: the 51 Ohm opto-LED resistor value in ADR-0001 and `docs/CONTROL_DESIGN.md`

## Context

HVM OPTO-100-05 datasheet, Rev B (`datasheets/HVM_OPTO-100.pdf`):

- Table, p. 2: "DC Current Transfer Ratio 0.15%" (typical, no test condition given); "LED Forward
  Current 400 mA" and "LED Max Input Voltage 5 V" (absolute max); "LED Voltage Input @100mA Current
  Drive 3.25 V" (typical).
- Graph "Current Transfer Ratio (Iin vs Iout)", p. 3: output current is 0 at about 0.04 A of LED
  current and rises linearly to about 410 uA at about 0.31 A. The slope, 410 uA / 0.27 A, is the
  0.15 % of the table. So the 0.15 % is an incremental ratio above a threshold of roughly 40 mA.
- Graph "Vin vs Iout", p. 3: output current is 0 at about 2.25 V and about 410 uA at about 5.0 V.
  At the input voltage the old design produces (about 3.0 V) this graph gives roughly 100 uA, so the
  two graphs disagree.

The June design used 51 Ohm from +5 V: (5 - ~2.9 V) / (51 + ~3.5 Ohm) = about 38 mA, and assumed a
proportional CTR (0.15 % x 38 mA = 57 uA). By the CTR graph, 38 mA sits at the threshold and gives
close to no output current, so a channel might not charge at all.

In the active-discharge topology the only standing load on an output is the 1 GOhm bleeder (5 uA at
5 kV), so any output current well above 5 uA reaches full voltage; the current sets the speed.

## Decision

R6, R14, R21, R22 (opto LED resistors) become **15 Ohm, 1206**, Panasonic ERJ-P08J150V (listed at
2/3 W by distributors; confirm on the Panasonic datasheet when ordering).

- LED current: 5 - V_in = 15 I with V_in about 2.9 + 3.5 I (a fit through the datasheet's 3.25 V at
  100 mA) gives I = 2.1 / 18.5 = 114 mA, a little less with the MOSFET's on-resistance. Inside the
  400 mA absolute maximum.
- Output current: about (0.10 to 0.114 - 0.04) A x 0.15 % = 90 to 110 uA by the CTR graph, higher by
  the Vin graph.
- Resistor dissipation: 0.114^2 x 15 = 0.19 W, about 30 % of the 2/3 W listing.

## Consequences

- Full 0 to 5 kV swing on a 1 nF DEA: 1 nF x 5 kV / 100 uA = about 50 ms per edge, either direction.
  The SMHV0550's 200 uA is the ceiling for any further speed-up (shared by both channels).
- +5 V load from the drivers: at most one opto per channel is on, so up to about 230 mA, on top of
  the HV module and the indicator LEDs.
- The footprint grows from 0603 to 1206; rev B places it in the same spot next to each opto.
- Bench test T1 measures output current against LED current on one OPTO-100. If the threshold is
  not real, 15 Ohm is still fine (faster, same limits); if the measured current at about 110 mA is
  below about 50 uA, revisit.
