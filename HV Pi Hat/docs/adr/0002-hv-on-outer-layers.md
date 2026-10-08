# ADR-0002: HV on the outer layers, inner layers voided, thick stackup

- Status: Accepted 2026-06-08 (the build log calls it "Decision A1"); stackup revised 2026-10-08
- Deciders: Anatol Gogoj
- Related: ADR-0003 (spacing basis), ADR-0004 (footprint)

## Context

Routing the 2-channel active-discharge HV zone needed about 2 mm spacing (ADR-0003). The first
idea was to bury HV on In1/In2 inside the FR4. Review found a 3-D hazard the 2-D DRC cannot see:
on a standard 1.6 mm 4-layer stack, the outer-to-inner prepreg is about 0.1 to 0.21 mm, so HV on
any layer faces adjacent-layer copper at up to about 24 kV/mm (5 kV / 0.21 mm).

## Decision

1. All five HV nets (`/HV_RAIL`, `/HV_CH1`, `/HV_CH2`, `/HV_CH1_DIS`, `/HV_CH2_DIS`) are routed on
   F.Cu and B.Cu only, 0.25 mm wide. Where two HV nets must cross, they use opposite outer layers.
2. In1.Cu and In2.Cu carry rule-area keepouts (no tracks, vias or fills) over the HV zone,
   board coordinates x 163.0 to 202.5 mm, y 94.5 to 142.0 mm.
3. Placement uses lanes: LV drivers on the left, the opto column in the middle (LED pins facing
   left, HV pins facing right), all HV parts on the right. LV signals do not cross the HV zone;
   the only LV copper inside it is the corridor along the SMHV0550 LV pin column (U1 pins 1 to 7).
4. The floating 5.4 mm copper pads on mounting holes H1 to H4 were removed (a floating plate near
   5 kV charges to an intermediate potential). The 3.1 mm plated ring remains.
5. Stackup: JLCPCB JLC04201H-7628D, 4 layers, 2.0 mm nominal. Layer by layer (mm): F.Cu 0.035,
   7628 x4 prepreg 0.864, In1 0.0152, core 0.2, In2 0.0152, 7628 x4 prepreg 0.864, B.Cu 0.035.
   Source: jlcpcb.com/impedance, 2.0 mm tab, read 2026-10-08. This is encoded in the board file.

The June version of this decision asked for a 2.0 to 2.4 mm custom stackup. JLCPCB does not offer
that for 4 layers: the capabilities page lists FR4 thicknesses up to 2.0 mm ("2.5 mm and above are
for 12+ layer PCBs only"), and the order form offers only six fixed 2.0 mm stackups for 4 layers
with no custom option. 7628D is the preset with the thickest outer prepreg, which is the dimension
this decision depends on.

## Consequences

- Measured on the board (2026-10-08, conservative shapes): the smallest 3-D gap between HV copper
  and non-HV copper on a different layer is 1.91 mm (HV_RAIL on B.Cu to the U1.9 GND annular ring on
  In2). An HV_RAIL track on B.Cu passes directly under a GND track on F.Cu with 1.96 mm of FR4
  between them. At 5 kV that is an average field of 2.5 to 2.6 kV/mm, before edge enhancement.
- Where CH1 and CH2 cross on opposite faces, the two can differ by the full 5 kV (one charged, one
  discharged): 5 kV across 1.96 mm of FR4, about 2.55 kV/mm. The June log set a long-term target of
  2 kV/mm or less but gave no source for it. Whether 2.5 kV/mm through FR4 is acceptable is part of
  ADR-0003.
- The 2-D DRC enforces the in-plane rules only. The through-board numbers above have to be
  re-measured after any HV re-route (the script used is described in `docs/TOOLING.md`).
- The order must name the stackup explicitly (JLC04201H-7628D). A default 2.0 mm order gets
  JLC04201H-7628, whose outer prepreg is 0.21 mm.
