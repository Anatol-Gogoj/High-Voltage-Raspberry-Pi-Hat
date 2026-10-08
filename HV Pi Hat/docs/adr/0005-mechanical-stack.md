# ADR-0005: Mechanical stack: standoff height, GPIO header, and the Pi 5 parts underneath

- Status: Accepted 2026-10-08 (Anatol): 20 mm standoffs.
- Deciders: Anatol Gogoj
- Related: ADR-0003 (bottom-face pot), ADR-0004 (HAT outline)

## Context

The HV zone is potted on both faces (ADR-0003), so the HAT's underside carries THT lead tails and a
pot over the right part of the board. What sits below it on a Raspberry Pi 5 was checked against the
official drawings (Pi 5 mechanical drawing RP-008347-DS-1, Active Cooler drawing RP-008187-DS-1,
HAT+ spec RP-008281-DS-1) and run through `tools/revb/PiKeepouts.py`. Assumptions: leads trimmed to
1.5 mm, bottom pot 3.0 mm thick.

| Pi 5 part | Under the HAT? | Height above Pi PCB | Room at 16 mm | Room at 20 mm |
|---|---|---|---|---|
| Active Cooler (fan directly under the pot) | yes, almost the whole board | 13.70 overall (drawing; pin tip to cap top) | **-0.7 mm** | 3.3 mm |
| PoE 2x2 header | yes, under the pot | 8.6 | 4.4 mm | 8.4 mm |
| Camera/display FPC connectors | yes, under the HV resistors | 4.1 | 8.9 mm | 12.9 mm |
| UART, RTC battery, PCIe FFC | yes | 4.2 to 4.5 | 8.6 mm or more | 12.6 mm or more |
| USB-A stacks, RJ45, fan connector | no: they start 5.7, 1.8 and 0.2 mm beyond the 65 mm edge | 15.9 / 14.0 / 4.5 | n/a | n/a |

The 13.70 mm cooler figure runs from the push-pin tip (below the Pi PCB) to the top of the pin cap,
so the real height above the PCB is lower; how much lower is not published.

The HAT+ spec (ch. 7) says: "provide at least 15mm board-to-board spacers; 16mm spacers are ideal. If
the underside of your HAT+ has components on it, use even larger spacers." It also says a HAT+
"should not interfere with access to camera, display, and PCIe flex connectors" (a recommendation).

The BOM's GPIO socket, Sullins PPTC202LFBN-RC, has an 8.51 mm body (DigiKey attributes; Sullins
series datasheet 0.335 in). On its own it cannot produce a 16 or 20 mm board-to-board gap, so the
header has to be re-specified whatever the standoff decision is.

## Options

1. **16 mm standoffs** (HAT+ default). Works only if the measured cooler top is 12.0 mm or less above
   the Pi PCB (16 - 3.0 pot - 1.0 margin).
2. **20 mm standoffs** with a GPIO stacking header to match. Clears the worst-case cooler by 3.3 mm,
   and follows the spec's advice for HATs with underside components.
3. **Passive heatsink instead of the Active Cooler** (the case heatsink is 4 mm). Clears easily at
   16 mm, at the cost of CPU cooling headroom.

## Decision

Option 2: **20 mm board-to-board standoffs**, with a GPIO header stack chosen to give exactly that gap.
This clears the worst-case Active Cooler height by 3.3 mm without needing the bench measurement, and
follows the HAT+ spec's advice to use larger spacers when the HAT has underside components. It
deviates from the spec's 16 mm "ideal"; the spec allows it.

## Consequences

- The GPIO header must be re-specified for a 20 mm gap (the PPTC202LFBN-RC gives about 11 mm).
- The fan intake faces up and sits under the pot at about 2 to 3 mm. Whether that costs enough
  cooling to matter is unknown; check SoC temperature under load with the HAT fitted.
- Camera/display flex access with the HAT fitted is not provided: those connectors sit under the HV
  resistor block, which a cutout like the M.2 HAT+'s would destroy. The left edge is kept free of
  parts and copper (`PcieNotch` in `tools/revb/RevBLayout.py`) so a PCIe flex notch stays possible.
