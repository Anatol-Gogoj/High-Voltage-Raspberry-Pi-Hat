# Locked design decisions — HV Pi Hat

Choices made with the user. Change only with a new explicit decision (and note it here).

| Area | Decision | Why |
|---|---|---|
| Form factor | **85 × 56 mm** (wider than the 65 mm standard HAT); committed | room for 5 kV creepage |
| Insulation | **Conformal coat** baseline; **pot/encapsulate** if more clearance needed | makes 5 kV fit a small board |
| HV spacing | **4 mm** clearance + creepage + edge on HV nets; **milled slots** between opposite polarities / channels / terminal pads | coated 5 kV figure; slots add creepage (KiCad treats slots as creepage barriers). Enforced in `HV Pi Hat.kicad_dru` |
| Max voltage | Design **headroom to 5 kV**; run variable/lower in firmware | |
| DEA load | **< 1 nF** | charge & discharge both fast |
| Bleeder | **100 MΩ** (R1/R2) | two-channel 200 µA budget; part is already 100 MΩ |
| HV output connector | **2-position terminal block per channel** + a **milled slot between its two pads** | 1×1 HV terminals hard to source; slot restores creepage |
| HV setpoint (PGM) | **PWM → RC → op-amp ×1.55 → PGM** (MCP6001-OT) | Pi has no DAC; 3.3 V PWM alone caps ~3.3 kV — gain to reach 0–5 kV |
| Current limit | **ILIMIT (pin 7) tied to 5 V** (disabled) | module is inherently 200 µA |
| Indicators | **Kept**, as a **parallel** branch off each channel MOSFET | the limit was *headroom*, not current — a series stack starved the opto |
| Discharge | **Active**: 2nd opto + series R per channel (independent charge / hold / discharge) | user request; controllable actuator relaxation |
| Safety bleeder | **1 GΩ always-on across each output, DNP-able** | fail-safe bleed-down when unpowered |
