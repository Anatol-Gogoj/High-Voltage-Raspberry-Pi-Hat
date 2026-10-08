# Architecture decision records

One decision per file, numbered in order. A new decision gets a new file; a changed decision gets
a new ADR that supersedes the old one, and the old one's status line points to it.

| ADR | Title | Status |
|---|---|---|
| [0001](0001-baseline-design-decisions.md) | Baseline design decisions (migrated from `DECISIONS.md`) | Accepted; rows partly superseded |
| [0002](0002-hv-on-outer-layers.md) | HV on the outer layers, inner layers voided, thick stackup | Accepted |
| [0003](0003-hv-spacing-basis.md) | HV spacing basis: encapsulate the HV zone | Accepted; prerequisites open |
| [0004](0004-board-footprint.md) | Board footprint: standard HAT outline (65 x 56.0 mm for a THT header) | Accepted; rev B meets it |
| [0005](0005-mechanical-stack.md) | Mechanical stack: 20 mm standoffs, GPIO header, Pi 5 parts underneath | Accepted; header not yet chosen |
