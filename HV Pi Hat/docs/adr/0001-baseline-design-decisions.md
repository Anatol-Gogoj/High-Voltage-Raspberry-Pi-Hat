# ADR-0001: Baseline design decisions

- Status: Accepted (2026-06-05 to 2026-06-07); some rows superseded, see the Status column
- Deciders: Anatol Gogoj
- Migrated from `docs/DECISIONS.md` on 2026-10-08. Full rationale for the 2026-06-07 rows is in
  `docs/AUTONOMOUS_BUILD_LOG.md`.

## Context

The original December 2025 schematic had functional bugs (floating `ILIMIT`, opto-LED resistors
too large to reach 5 kV, an indicator stack that starved the opto). `docs/REVIEW_FINDINGS.md`
records them. The decisions below fixed the circuit and set the board-level constraints.

## Decisions: circuit and board (2026-06-05)

| Area | Decision | Why | Status |
|---|---|---|---|
| Form factor | 85 x 56 mm, wider than the 65 mm HAT | Room for 5 kV creepage | Superseded by ADR-0004 (target the standard HAT+ outline) |
| Insulation | Conformal coat as baseline; pot or encapsulate if more margin is needed | Lets 5 kV fit a small board | Current |
| HV spacing | 4 mm clearance, creepage and edge on HV nets, milled slots between polarities | Coated 5 kV figure | Superseded by ADR-0003. Slots were not used: KiCad treats slot edges as board edge, which conflicts with the HV-to-edge rule |
| Max voltage | Hardware headroom to 5 kV; run lower in firmware | | Current. The build log puts the true ceiling at about 4.68 kV from a 3.3 V PWM through the x1.56 stage |
| DEA load | Less than 1 nF | Charge and discharge both fast | Current |
| Discharge resistor | 100 MOhm (R1, R2, Murata MHR0317SA107F70) | Two-channel 200 uA budget | Current, reused as `R_dis` |
| HV output connector | 2-position terminal block per channel with a slot between pads | | Superseded twice; see the connector row below |
| HV setpoint (PGM) | PWM, RC filter, MCP6001 op-amp x1.55, module PGM | Pi has no DAC; 3.3 V PWM alone caps near 3.3 kV | Current |
| Current limit | `ILIMIT` (pin 7) tied to 5 V | Module is inherently 200 uA | Current |
| Indicators | Kept, as a parallel branch off each channel MOSFET | A series stack starved the opto | Current |
| Discharge | Active: second opto plus series R per channel | Independent charge, hold, discharge | Current |
| Safety bleeder | 1 GOhm always on across each output, DNP-able | Fail-safe bleed-down when unpowered | Current. Populated by default (finding F-9) |

## Decisions: autonomous build pass (2026-06-07)

| Area | Decision | Why | Status |
|---|---|---|---|
| Indicator branch | +5V, R (470 Ohm), LED, MOSFET drain | The opto-LED node left about 0.1 V headroom; the drain node gives about 6 mA | Current |
| Input bulk caps | Keep 47/1/0.1 uF on +5V; add C5 0.1 uF op-amp decoupling | A ferrite is nearly transparent at the module's 45 to 80 kHz switching | Current |
| Custom symbol pin types | MOSFET SRC/DRAIN, opto pins, module HVRTN set to passive; ILIMIT set to input | Cleared false output-to-output ERC errors | Current |
| Power flags | PWR_FLAG on +5V and GND | Board is powered from the Pi | Current |
| HV netclass binding | `.kicad_pro` pattern `/HV_*` maps to `HV_5kV` | Survives net renames | Current |
| Passive footprints | 0603 for the 51 Ohm opto-LED resistors and other passives; 1206 for 47 uF | Power margin and hand soldering | Current |
| HV output connector | 1x2 screw terminal, 10.16 mm pitch (`TerminalBlock_RND_205-00241`), pad 1 = GND, pad 2 = HV out | SHV-R rejected: about 34 mm footprint and only 3.5 kV continuous | Current on the board. The part choice and the soldered-lead alternative are in `docs/HV_CONNECTOR_OPTIONS.md` and are tied to ADR-0004 |
