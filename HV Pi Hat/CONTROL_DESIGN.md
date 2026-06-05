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
                    R_dis 100M     R_safety 1G (DNP, always-on fail-safe)
                         │              │
                  [OR_dis] HVIN         │
                  [OR_dis] HVOUT ───────┴──── GND ;  J pin1 → GND → DEA(−)

 Charge drive:    +5V ┬ R_opto_chg 51Ω ─ OR_chg LED(+→−) ┐
                      └ R_ind 470Ω ─ D_chg(A→K) ─────────┴ Q_chg DRAIN
                                       Q_chg SRC ─ GND ;  GATE ← GPIO_chg (100Ω series, 10k→GND)
 Discharge drive: +5V ┬ R_opto_dis 51Ω ─ OR_dis LED(+→−) ┐
                      └ (opt) R_ind2 470Ω ─ D_dis ────────┴ Q_dis DRAIN
                                       Q_dis SRC ─ GND ;  GATE ← GPIO_dis (100Ω series, 10k→GND)
```
- **Charge:** assert GPIO_chg → OR_chg conducts → DEA charges toward the rail (set by PGM).
- **Hold:** both optos off → DEA holds (slow bleed only through R_safety).
- **Discharge:** assert GPIO_dis → OR_dis conducts → DEA dumps through R_dis to GND.
- `R_dis` 100 MΩ → ~100 ms dump for <1 nF; drop to ~10 MΩ for a faster (~10 ms, opto-limited) dump.
- `R_safety` ~1 GΩ (Murata MHR0317SA108F70) → τ≈1 s; fail-safe bleed when unpowered. DNP if undesired.
- Opto = HVM OPTO-100 (10 kV, CTR 0.15%); `R_opto_*` 51 Ω → I_LED≈38 mA → Iout≈57 µA (≥50 µA needed for 5 kV into 100 MΩ).

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
1× op-amp + RC/feedback/decoupling, 2× R_safety 1GΩ (DNP). Reuse R1/R2 (100 MΩ) as R_dis.
Change: R3/R4 200→51Ω (opto charge), R5/R6 300→470Ω (indicator). Optional: 2× discharge indicators.
