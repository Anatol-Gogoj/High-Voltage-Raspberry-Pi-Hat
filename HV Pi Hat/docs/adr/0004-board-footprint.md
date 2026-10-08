# ADR-0004: Board footprint: target the standard HAT+ outline

- Status: Accepted 2026-10-08. Rev B (issue #6) meets the outline; rev A (85 x 56 mm) did not. The
  placement study used 65 x 56.5 with the extra 0.5 mm on the wrong edge; rev B corrects it.
- Deciders: Anatol Gogoj
- Supersedes: the "Form factor 85 x 56 mm" row of ADR-0001
- Related: ADR-0002 (layer strategy), ADR-0003 (spacing basis)

## Position

Anatol is pushing to keep this board in the same footprint as a standard Raspberry Pi HAT:
65 x 56.5 mm with the standard mounting-hole pattern. The 85 x 56 mm outline used in rev A was a
concession to fit the HV zone at the spacing in force at the time. It is not the intended end
state, and further layout work should move toward the standard outline rather than away from it.

## Context

What the Raspberry Pi HAT+ specification says (build 2024-12-05,
https://datasheets.raspberrypi.com/hat/hat-plus-specification.pdf, and the legacy drawing
https://github.com/raspberrypi/hats/blob/master/hat-board-mechanical.pdf):

- Outline 65 x 56.5 mm (HAT+ figures 2 and 3); 3 mm corner radius (legacy drawing).
- Four M2.5 holes, "DRILLED TO 2.75mm +/- 0.05mm", on a 58 x 49 mm pattern, 3.5 mm from the edges.
  Holes ideally non-plated; if plated, isolated and not tied to GND.
- Standoffs: "provide at least 15mm board-to-board spacers; 16mm spacers are ideal".
- The hard requirements are the 40-way header including the ID pins, at least one hole aligned
  with a Pi hole, and the ID EEPROM of chapter 6. The spec is "less prescriptive about HAT
  physical dimensions", so an oversized board can still be a HAT+. The standard outline is
  therefore a design goal here (fit, stacking, cases, and no overhang over the Pi 5 USB and RJ45
  connectors), not a compliance requirement.

Rev A as built (measured from the board file 2026-10-08):

- Outline 85.05 x 56.05 mm, x 117.475 to 202.525, y 85.975 to 142.025 (board coordinates).
- Holes H1 to H4 at (121, 89.5), (179, 89.5), (121, 138.5), (179, 138.5): already the standard
  58 x 49 mm pattern, 3.5 mm from the left and top edges. A standard outline would end at
  x = 182.5 mm.
- Beyond x = 182.5 today: both output terminals J3 and J4, the right half of the SMHV0550 module
  (pins at x 170.95 to 187.46; body 0.85 x 0.85 in, about 21.6 mm square, per `docs/BOM_SOURCED.md`)
  and the right-hand pads of the four 17.6 mm HV resistors R1, R2, R25, R26 (pads at x 172.4 and
  187.6).
- The 20 mm extension overhangs the Pi 5 USB-A and RJ45 end, which is why rev A asks for 20 mm or
  taller standoffs instead of the 16 mm the spec recommends. The Pi 5 mechanical drawing does not
  publish connector heights, so that number is not verified.
- No ID EEPROM is fitted, and the GPIO map avoids ID_SD/ID_SC. To call the board a HAT+, an EEPROM
  must be added regardless of size.

## Decision

Target the standard HAT outline with the standard hole pattern and 3 mm corners. For this board's
through-hole GPIO header that is **65 x 56.0 mm**: the legacy HAT drawing reads "56.5mm FOR SMT STYLE
GPIO HEADER OTHERWISE 56.0mm FOR THROUGH HOLE HEADER", with the bottom holes 3.5 mm from the bottom
edge (the extra 0.5 mm of the SMT variant is on the header edge). Each mounting hole keeps a 6.2 mm
land free of other copper ("MIN. 6.2mm and EITHER ISOLATED COPPER OR BARE BOARD"). Rev A stays
85 x 56 mm as a prototype until a layout that meets the target and ADR-0003 exists.

## Consequences and the path to the standard outline

The HV zone has to lose about 20 mm of width: from x 163 to 202.5 today (39.5 mm) to x 163 to 182.5
(19.5 mm) if the LV and opto lanes stay where they are. The SMHV0550 body alone is 21.6 mm wide, so
the lanes have to compact too. Levers, in recommended order:

1. Replace the J3/J4 screw terminals with direct-soldered HV silicone leads and a strain relief.
   `docs/HV_CONNECTOR_OPTIONS.md` already ranks this first for a lab build, and it removes both
   terminals from the outline.
2. Compact the LV and opto lanes leftward to give the module a full-width slot inside x 182.5.
3. Look for physically shorter HV resistors for R_dis and R_safety than the 17.6 mm MHR0317
   bodies. No candidate part has been sourced yet.
4. Only if 1 to 3 fail: give up active discharge on one or both channels, which reverses an
   ADR-0001 decision.

Feasibility (2026-10-08): the placement study in `studies/hatplus/` (issue #4) routes the full
two-channel active-discharge circuit inside the 65 x 56.5 mm outline with the HV zone potted, using
levers 1 and 2 only, at both 2 mm and 3 mm HV spacing. It is a scripted feasibility layout, not a
finished one; its README lists what remains.

The spacing basis (ADR-0003) pulls the other way. Every millimeter added to the HV rule makes the
standard outline harder, so the placement study should run at the spacing ADR-0003 settles on,
not at today's provisional 2 mm.
