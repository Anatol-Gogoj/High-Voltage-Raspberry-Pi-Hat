# Fabrication outputs

No Gerbers or drill files are committed, on purpose. This is a 5 kV board, and outputs stay out of
the repo until all of these hold:

1. ADR-0003 (HV spacing basis) is accepted and the board passes DRC against it.
2. A qualified human EE has reviewed the schematic and the HV layout, including the through-board
   distances from `tools/HvInterlayer.py`.
3. The order specifies the ADR-0002 stackup (JLCPCB JLC04201H-7628D, 2.0 mm), not the default.

The Gerbers that used to sit in the project root and in `HV Pi Hat.zip` / `.7z` were from the
December 2025 design, which had the bugs listed in `docs/REVIEW_FINDINGS.md`. The
`preliminary_DO_NOT_FAB/` set was from an unroutable June 2026 intermediate. Both were removed on
2026-10-08 and remain in git history.

`BOM.csv` is generated from the schematic (`docs/TOOLING.md`); sourcing is in `docs/BOM_SOURCED.md`.
