# ADR-0007: HAT+ compliance: ID EEPROM, underside GPIO socket, unplated mounting holes

- Status: Accepted 2026-10-08 (Anatol: "go for your recommendations")
- Deciders: Anatol Gogoj
- Related: ADR-0004 (outline), ADR-0005 (stack height)

## Context

Raspberry Pi HAT+ specification (RP-008281-DS-1) and the legacy HAT mechanical drawing
(github.com/raspberrypi/hats, hat-board-mechanical.pdf) require or recommend:

- Ch. 3: an ID EEPROM read at boot; "Use a 24Cxx 3.3V I2C EEPROM", "16-bit addressable", "with a
  write protect (WP) pin that protects the entire device memory", no clock stretching, no paged
  addressing. Recommended part: "OnSemi CAT24C32". Write protect: "connect the EEPROM write protect
  pin to a test point on the board pulled-up to 3.3V with a 1KΩ resistor".
- Ch. 2 (important note): "The only permitted connections to the ID_SC and ID_SD (GPIO0 and GPIO1)
  pins are an ID EEPROM and the required 3.9KΩ pull-up resistors to 3.3V."
- Ch. 3.1: address 101_00XY; XY = 00 is the Standard class (a HAT+ that uses GPIOs 2 to 27).
- Ch. 2.2: a HAT+ "must be electrically compatible with the STANDBY state" (only 5 V powered).
- Drawing: mounting holes "should ideally be non-plated", drilled 2.75 +/- 0.05 mm, land at least
  6.2 mm of isolated copper or bare board.

## Decision

1. **ID EEPROM** U3 = OnSemi CAT24C32 (SOIC-8; the KiCad 24LC16 symbol supplies the 24Cxx pinout).
   A0 to A2 to GND (address 0x50, Standard class). R27/R28 3.9 kOhm pull-ups on ID_SD/ID_SC to
   +3V3 (header pin 1), R29 1 kOhm WP pull-up with test point TP1, C6 100 nF decoupling.
2. **GPIO socket on the underside**: GPIO1 uses the bottom-side PinSocket_2x20 footprint (same pad
   positions as before, checked pad by pad); the part is the elevated socket of ADR-0005.
3. **Mounting holes** H1 to H4: unplated 2.75 mm (`HV_Footprints:MountingHole_2.75mm_M2.5_NPTH_HAT`)
   with a 6.2 mm copper-free land kept by rule areas. This also removes the last floating copper
   rings near the potted zone.

## Consequences

- STANDBY: with only 5 V up, the GPIO pins and 3.3 V are unpowered. The MOSFET gates have 10 kOhm
  pull-downs and PGM is held at 0 V by R8 (100 kOhm), so the HV module is programmed to 0 V and no
  opto conducts. Bench test T7 checks this.
- The EEPROM must be programmed (product UUID, vendor and product strings, and a Device Tree overlay
  name are required or recommended by ch. 3) before the board can be called a HAT+. The overlay that
  configures GPIO5/6/16/26 and the GPIO12 PWM is a firmware task, not yet written.
- Schematic parity: H1 to H4 remain board-only footprints (no schematic symbols), as in rev A.
