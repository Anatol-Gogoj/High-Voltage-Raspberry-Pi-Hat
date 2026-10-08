# HV Pi Hat — design review findings (2026-06-05)

> Status: these issues are **resolved in `CONTROL_DESIGN.md`** and implemented in the schematic
> (ERC 0 errors). The "Decisions pending" list at the end was answered in
> `adr/0001-baseline-design-decisions.md`. Kept as the record of *why* the redesign was made.

Source: KiCad netlist + datasheets (see `datasheets/`). Architecture concept is sound
(SMHV0550 5 kV/200 µA module → per-channel OPTO-100 photo-coupler as charge switch →
DEA, with a bleeder for discharge, MOSFET driving the opto LED, optical control isolation).
But as wired the control/drive path will **not** produce useful HV. Issues below, by priority.

## As-wired drive path (per channel)
`+5V → R6/R5 (300Ω) → D1/D3 (indicator LED) → R3/R4 (200Ω) → OPTO LED → Q1/Q2 (low-side, GPIO gate) → GND`
`SMHV HVOUT (rail) → OPTO photodiode → DEA(+) [J3/J4 pin2];  DEA(−)[pin1] → R1/R2 (100MΩ) → GND`

## Critical

**A. SMHV `ILIMIT` (pin 7) is floating.** Datasheet: pin 7 is the current-limit *input*
(0–1 V → 0–100 % of rated current; **tie to 5 V to disable**). Floating ≈ 0 V ⇒ ~0 % limit
⇒ module sources ~no current. → **Tie pin 7 to 5 V** (disable) or to a divider for a set limit.

**B. Opto LED is starved.** With the indicator LED *in series* and R=500 Ω total, the drop is
~2 V (D1) + ~2.9 V (opto LED) ≈ 4.9 V of the 5 V rail → only ~0.2 mA through the opto LED.
At CTR 0.15 % that's ~0.3 µA out → < ~50 V at the output. Even without the indicator (500 Ω),
only ~4 mA → ~6 µA → < ~0.7 kV.
→ **Remove the indicator from the series path** and **drop the opto-LED resistor to ~60 Ω**
(I_LED ≈ 33 mA → Iout ≈ 50 µA → can drive 100 MΩ to 5 kV). Size: R ≈ (5 − 2.9)/I_LED.

**C. Bleeder R1/R2 is in the wrong leg.** It sits between the DEA return pin and GND (in series
with the actuator), so the HV+ node has **no discharge path** when the opto is off — no actuator
relaxation and **no bleed-down safety**. → **Re-wire R1/R2 across the HV output** (HV+ node → GND),
and tie the DEA return pin directly to GND. Then τ = R·C = 100 MΩ × <1 nF ≈ <100 ms.

## Major

**D. PGM control is a raw 3.3 V PWM, unfiltered.** SMHV `PGM` (pin 3) wants 0–5 V analog
(0–5 V → 0–full scale). It's driven straight from GPIO12/PWM0 with no RC filter.
- No filter ⇒ the module sees a square wave (ripple/instability on HV out).
- 3.3 V max ⇒ only ~66 % of full scale ⇒ **~3.3 kV ceiling** even if filtered.
→ Add an RC low-pass (e.g. 10 kΩ + 1 µF). For the **full 5 kV**, add a 3.3 V→5 V gain stage
(rail-to-rail op-amp ×~1.55 from 5 V) **or** use an I²C DAC (e.g. MCP4725) at 5 V for clean analog.

## Housekeeping

- **Decoupling / bulk:** none present. Add input bulk cap at SMHV Vin (it switches 45–80 kHz,
  draws up to ~350 mA) + local decoupling; budget ~0.5 A from Pi 5 V (module + 2 opto LEDs).
- **Ch-1 enable uses GPIO1/ID_SC (pin 28)** — a HAT-ID-EEPROM pin. Move to a normal GPIO.
- **Vmon/Imon (pins 5/6) unconnected** — optional: route to an ADC for telemetry.

## GPIO map (current)
| Function | GPIO | Pin |
|---|---|---|
| SMHV PGM (HV setpoint) | GPIO12 / PWM0 | 32 |
| Ch1 enable (Q1 gate) | GPIO1 / ID_SC ⚠ | 28 |
| Ch2 enable (Q2 gate) | GPIO26 | 37 |

## Decisions pending
1. Full 5 kV (adds PGM level-shift/DAC + opto-LED R sized for 5 kV) vs accept ~3 kV (RC filter only)?
2. Current limit: disable (tie 5 V) vs set a protective limit (divider on pin 7)?
3. Keep per-channel indicator LEDs (moved onto the enable GPIO) or drop them?
