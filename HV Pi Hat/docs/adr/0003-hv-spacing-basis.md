# ADR-0003: HV spacing basis

- Status: Accepted 2026-10-08 (Anatol): option 2, encapsulate the HV zone. Fabrication stays
  blocked until the prerequisites under "Decision" are done and a qualified EE has signed off.
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

## Decision

Option 2: encapsulate the HV zone (IEC 60664-3 type 2 protection, insulation treated as solid
insulation) and qualify it by test. It is the only sourced route that keeps the board near the
standard HAT+ outline (ADR-0004) without resting on an unsourced spacing figure.

Prerequisites before fabrication:

1. Get IEC 60664-3 Table 1 (type 2 minimum spacings) from the standard itself and set the DRC rules
   for the potted zone to it.
2. Pick a potting compound with a published dielectric strength and, given the extreme-environment
   work, a published outgassing figure.
3. Define the qualification test: DC withstand voltage, duration, and partial-discharge threshold,
   on a potted coupon or a first article.
4. Name the reviewing EE.

## Potting compound (prerequisite 2): shortlist, 2026-10-08

Recommended: **DOWSIL 93-500 Space Grade Encapsulant, primed.** Fallback: NuSil CV-2500.

| | DOWSIL 93-500 | NuSil CV-2500 | Stycast 2850FT + CAT 23LV |
|---|---|---|---|
| Chemistry | addition-cure silicone elastomer | addition-cure silicone elastomer | filled epoxy |
| Dielectric strength | "475 volts/mil" (19 kV/mm) | not in the TDS | 14.8 kV/mm |
| Dk | 2.6 at 100 Hz | not in the TDS | 5.36 at 1 MHz |
| Mixed viscosity | 8,100 cP | Part A 8,000 cP | 5,600 cP |
| Cure | 24 h at 25 C or 10 min at 100 C | 15 min at 150 C | 16 to 24 h at 25 C |
| Low temperature | TDS "-45 to 200°C" long term (2001 sheet: -115 C) | DMA Tg -130 C | Tg 40 to 55 C |
| ASTM E595 TML/CVCM | TDS 0.14/0.01; NASA DB 2018 lots 0.08/0.01 and 0.08/0.02 | TDS 0.05/0.01; NASA DB 0.06/0.01 | NASA DB 0.53/0.01, 0.49/0.01 |
| Primer | "priming will be required for many" (DC 1200 or P5200) | CF1-135 | none named |
| Availability | Ellsworth, in stock, 110 g kit about $1,300 | 50 to 500 g kits, no stock found | DigiKey/Mouser |

Sources: Dow TDS 11-1811-01 A and Form 10-951-01, NuSil CV-2500 Rev. B, Henkel Stycast 2850FT TDS,
NASA GSFC outgassing database (etd.gsfc.nasa.gov/capabilities/outgassing-database). Ruled out as
supplied by the NASA screen (CVCM 0.10 % or less): Sylgard 184 (0.92/0.40, 1.61/0.78) and RTV655
(3.55/0.96); only devolatilized lots pass.

Why 93-500: full electrical data, recent NASA entries, and stock. The bulk field is not the limit
(5 kV over 3 mm is 1.7 kV/mm, about 11 times below 19 kV/mm); the interfaces are. Its low Dk helps:
in a thin void across the field the void field is about the compound's Dk times the bulk field, 2.6x
for 93-500 against 5.4x for the epoxy. The epoxy's Tg sits inside the operating range and it is rigid.
About 15 g per board (both faces), so one 110 g kit covers a few boards plus test coupons. The cost
is the main drawback; Anatol decides the purchase.

## Interim layout rules (until prerequisite 1 is done)

These are working assumptions for placement and routing, not a qualified basis:

- Every piece of HV copper (pads, tracks, vias, and the THT solder joints on the far face) sits
  inside the potted zone. The THT HV parts put solder joints on B.Cu, so the zone is potted on
  both faces.
- Inside the zone: 2 mm minimum from HV copper to any other copper, the value rev A already meets.
  Placement studies also report how the layout behaves at 3 mm.
- The pot edge sits at least 3 mm outside any HV copper on both faces. HV leaves the zone only as
  insulated wire (the DEA leads), never as copper on the board surface. This rules out the J3/J4
  screw terminals: a terminal inside the pot cannot be used, and one outside it puts HV copper on
  an open surface. The outputs become soldered HV leads with strain relief, the first choice in
  `docs/HV_CONNECTOR_OPTIONS.md`.
- Copper that is not HV may sit inside the zone; the opto LED pins and the module's LV pins do.
- The bottom-face pot must stay clear of the Pi 5 below. HAT+ recommends 16 mm standoffs; the
  bottom pot height budget is not yet known.

`HV Pi Hat.kicad_dru` keeps the 2 mm rules until prerequisite 1 replaces them, and
`fab/README.md` keeps fabrication blocked.
