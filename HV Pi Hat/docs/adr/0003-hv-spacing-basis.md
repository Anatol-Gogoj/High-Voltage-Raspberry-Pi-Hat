# ADR-0003: HV spacing basis

- Status: Proposed 2026-10-08. Needs Anatol's decision and a qualified EE's sign-off. Until then
  the board's 2 mm rules are provisional and the board must not be fabricated.
- Deciders: Anatol Gogoj (owner), reviewing EE (to be named)
- Supersedes: the "HV spacing" row of ADR-0001 (4 mm, then relaxed to 2 mm on 2026-06-08)
- Related: ADR-0002 (layer strategy), ADR-0004 (footprint)

## Context

`HV Pi Hat.kicad_dru` holds HV nets to 2 mm air clearance and 2 mm creepage (4 mm to the GND pour,
1 mm to drilled holes). The June build log justified 2 mm with "under IEC 60664 a coated surface
(pollution degree 1) drops the 5 kV creepage requirement to about 2 mm". No table was cited, and
the claim does not survive a lookup. Rev A passes DRC at 2 mm with zero HV violations, so DRC
cleanliness says nothing about whether 2 mm is adequate.

## What the standards say at 5 kV DC

| Source | Condition | Required | How it was read |
|---|---|---|---|
| IEC 60664-1:2020 Table F.5 | Creepage, pollution degree 1, any material (the printed-wiring columns stop at 1000 V) | **20 mm** (16 mm at 4000 V) | KiCad `pcb_calculator/calculator_panels/iec60664.cpp`, which cites "IEC60664-1 : 2020-05 Table F.5"; checked 2026-10-08. Secondary |
| IEC 60664-1:2020 Table F.5 | Creepage, pollution degree 2, material group IIIa/IIIb (FR4; Isola 370HR lists CTI 175 to 249 V) | **50 mm** | Same file. Secondary |
| IEC 60664-1:2020 Table F.8 | Clearance to withstand steady-state peaks, 5.0 kV, case A (inhomogeneous field, which PCB traces are) | **5.7 mm** (case B, homogeneous: 1.5 mm) | Same file. Secondary |
| IPC-2221B Table 6-1 | A5, conformal coating over the assembly: 0.8 mm + 0.00305 mm/V x (5000 - 500) V | **14.5 mm** | Altair Pollex transcription. Secondary. IPC-2221C (2023) changed the coated columns; values not found |
| IPC-2221B Table 6-1 | B1, internal conductors: 0.25 mm + 0.0025 mm/V x 4500 V | 11.5 mm | Same |
| IEC 60664-3 | Type 1 protection (coating) | Reduces the covered surface to pollution degree 1, so the 20 mm row applies. Requires a qualified coating covering 100 % of the gap | IEC webstore abstract. Primary |
| IEC 60664-3 | Type 2 protection (coating or potting acting as solid insulation) | Treated as solid insulation; minimum spacings are in its Table 1. **Table 1 values not found.** Qualified by test | IEC webstore abstract. Primary |
| IEC 61010-1 | Lab equipment, coatings to reach pollution degree 1 | Must meet Annex H. Insulation sizing applies where it protects against a hazard | Test report form text. Secondary |

Through the board, no standard found gives a long-term DC kV/mm limit for FR4. Isola 370HR lists
54 kV/mm short-term electric strength (IPC-TM-650 2.5.6.2A), and that method notes values "decrease
with increasing specimen thickness". Rev A has 1.96 mm of FR4 at its HV crossings, about 2.55 kV/mm
at 5 kV (ADR-0002).

IEC 60664-1's scope is equipment rated up to AC 1000 V or DC 1500 V, but it states that "higher
voltages can exist in internal circuits", and its tables extend past 5 kV.

## What it means for rev A

Re-running DRC on rev A with a coat-only basis (6 mm clearance, 20 mm creepage on HV nets) gives
**354 HV violations** (200 creepage, 154 clearance). A coat-only basis cannot be met on this board
or on the standard HAT+ outline of ADR-0004. The 2-channel active-discharge circuit needs on the
order of 20 mm between HV nodes, more than a third of the board's 56 mm height.

## Options

1. **Coat only (type 1).** 20 mm creepage, 6 mm clearance, qualified coating. Requires a board several
   times larger, or dropping channels or active discharge. Incompatible with ADR-0004.
2. **Encapsulate the HV zone (type 2 protection / solid insulation).** Pot the HV area (module
   outputs, optos' HV side, HV resistors, terminations) so the insulation is the potting compound,
   not air and a surface. Spacing then comes from IEC 60664-3 Table 1 and a qualification test (DC
   withstand above 5 kV plus partial discharge) instead of the creepage table. Needs a potting dam,
   a compound choice, and an outgassing check if the board will ever go to vacuum. ADR-0001 already
   lists "pot or encapsulate if more margin is needed".
3. **Documented functional-insulation deviation.** Keep coating and about 2 mm, classify HV-to-GND as
   functional insulation inside a closed enclosure, and justify by test. Whether the HV can be
   classed as functional depends on whether it is accessible: the DEA and its leads are outside the
   board, so this needs its own analysis under IEC 61010-1 clause 6. Weakest of the three.

## Recommendation

Option 2. It is the only sourced route that keeps the board near the standard HAT+ outline
(ADR-0004) and does not rest on an unsourced 2 mm figure. Before accepting it:

1. Get IEC 60664-3 Table 1 (type 2 minimum spacings) from the standard itself and set the DRC rules
   to it for the potted zone.
2. Pick a potting compound with a published dielectric strength and, given the extreme-environment
   work, a published outgassing figure.
3. Define the qualification test: DC withstand voltage, duration, and partial-discharge threshold,
   on a potted coupon or a first article.
4. Name the reviewing EE.

Until this ADR is accepted, the 2 mm rules in `HV Pi Hat.kicad_dru` stay as a placeholder so DRC
keeps checking connectivity and relative spacing, and `fab/README.md` keeps fabrication blocked.
