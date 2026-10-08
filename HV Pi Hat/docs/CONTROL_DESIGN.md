# HV Pi Hat — corrected control/drive design (to implement)

Resolves `REVIEW_FINDINGS.md`. Decisions locked 2026-06-05:
PGM = RC-filtered PWM + op-amp ×1.55 (full 5 kV) · ILIMIT tied to 5 V ·
indicators = **parallel** branches off each MOSFET · **active charge AND discharge**
(separate opto per direction) · high-value always-on safety bleeder (DNP-able).

## Per-channel block (×2)
```
        SMHV HVOUT (rail, shared by both channels)
          │
   [OR_chg] HVIN→HVOUT ──┬──────────────┬───────── J pin2 (HV+) → DEA(+)
                         │              │
                    R_dis 100M     R_safety 1G (populated, always-on fail-safe)
                         │              │
                  [OR_dis] HVIN         │
                  [OR_dis] HVOUT ───────┴──── GND ;  J pin1 → GND → DEA(−)

 Charge drive:    +5V ┬ R_opto_chg 15Ω ─ OR_chg LED(+→−) ┐
                      └ R_ind 470Ω ─ D_chg(A→K) ─────────┴ Q_chg DRAIN
                                       Q_chg SRC ─ GND ;  GATE ← GPIO_chg (100Ω series, 10k→GND)
 Discharge drive: +5V ┬ R_opto_dis 15Ω ─ OR_dis LED(+→−) ┐
                      └ (opt) R_ind2 470Ω ─ D_dis ────────┴ Q_dis DRAIN
                                       Q_dis SRC ─ GND ;  GATE ← GPIO_dis (100Ω series, 10k→GND)
```
- **Charge:** assert GPIO_chg → OR_chg conducts → DEA charges toward the rail (set by PGM).
- **Hold:** both optos off → DEA holds (slow bleed only through R_safety).
- **Discharge:** assert GPIO_dis → OR_dis conducts → DEA dumps through R_dis to GND.
- `R_dis` 100 MΩ → ~100 ms dump for <1 nF; drop to ~10 MΩ for a faster (~10 ms, opto-limited) dump.
- `R_safety` ~1 GΩ (Murata MHR0317SA108F70) → τ≈1 s; fail-safe bleed when unpowered. Populated by default; DNP only if a passive bleed is unwanted (finding F-9).
- Opto = HVM OPTO-100 (10 kV, CTR 0.15% incremental above a ~40 mA threshold per the datasheet graph); `R_opto_*` **15 Ω 1206** → I_LED ≈ 110 mA → Iout ≈ 90–110 µA (ADR-0006). The old 51 Ω gave ~38 mA, at the threshold. The only standing output load is the 1 GΩ bleeder (5 µA at 5 kV); Iout sets the charge/discharge speed (~50 ms per 0–5 kV edge at 1 nF).

## Shared: HV setpoint (PGM) — full 0–5 kV
```
GPIO12/PWM0 ─ R 10k ─┬──────────┬─ V+ op-amp (RRIO, 5V; e.g. MCP6001)
                     C 1µF      R 100k          OUT ─────────── SMHV PGM (pin3)   (opt: 100nF PGM→GND)
                     │          │   feedback: Rf 5.6k (OUT→V−), Rg 10k (V−→GND) ⇒ gain 1.55
                    GND        GND
```
- 100k pulldown ⇒ PGM=0 (HV off) at boot. RC corner ≈16 Hz; run PWM ≥20 kHz. Op-amp: 0.1 µF decoupling.

## Shared: SMHV module
- VIN(1)=+5V with **47 µF + 1 µF + 0.1 µF** bulk/decoupling; ferrite bead from Pi 5 V → module 5 V.
- GND(2), HVRTN(9) = GND.  **ILIMIT(7) → 5 V** (full output).  PGM(3) ← op-amp.  Vmon/Imon(5/6) → ADC (optional).
- HVOUT(8) = rail → OR_chg HVIN of both channels.

## GPIO map
| Function | GPIO | Pin |
|---|---|---|
| HV setpoint (PGM) | GPIO12/PWM0 | 32 |
| Ch1 charge | GPIO5 | 29 |
| Ch1 discharge | GPIO6 | 31 |
| Ch2 charge | GPIO26 | 37 |
| Ch2 discharge | GPIO16 | 36 |

## BOM vs. current
Add: 2× OPTO-100 (discharge), 2× TN0610 (discharge), 2× 51Ω + 2× 100Ω + 2× 10k (discharge driver),
1× op-amp + RC/feedback/decoupling, 2× R_safety 1GΩ (populated). Reuse R1/R2 (100 MΩ) as R_dis.
Change: R3/R4 200→51Ω (opto charge), R5/R6 300→470Ω (indicator). Optional: 2× discharge indicators.

## HAT+ ID EEPROM (ADR-0007)
U3 CAT24C32 on ID_SD/ID_SC (header pins 27/28), A0..A2 = GND (address 0x50, Standard class), R27/R28 3.9 kΩ pull-ups to +3V3 (header pin 1), WP pulled up by R29 1 kΩ with test point TP1 (drive low to program), C6 100 nF. Nothing else may connect to ID_SD/ID_SC (HAT+ spec ch. 2).
