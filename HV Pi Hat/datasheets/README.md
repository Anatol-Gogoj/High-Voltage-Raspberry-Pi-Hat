# Datasheets — HV Pi Hat

Local copies of datasheets for the key parts in this design. Pulled 2026-06-05.

| Part | Ref(s) | Role | Key specs | File | Source |
|---|---|---|---|---|---|
| HVM SMHV0550 | U1 | 5 kV programmable HV DC-DC module | 0–5 kV out, **200 µA** max, 5 V in (<350 mA), Program 0–5 V, Vmon/Imon 0–1 V, Ilimit (tie 5 V to disable), non-isolated (HVRTN=GND), 45–80 kHz | `HVM_SMHV_series.pdf` | [hvmtech.com/smhv-series](https://www.hvmtech.com/smhv-series) |
| HVM OPTO-100-05 | OR1–OR4 | HV opto-coupler (charge path / HV switch) | **10 kV** standoff, **CTR 0.15%**, LED Vf 2.9–3.25 V, LED 400 mA max, turn-on/off 2 µs, internal current-limit R | `HVM_OPTO-100.pdf` | [hvmtech.com/opto100](https://www.hvmtech.com/opto100) |
| Murata MHR0317SA107F70 | R1, R2 | HV bleeder / discharge resistor | **100 MΩ** (code 107), 0317 size, axial HV chip | `Murata_MHR0317SA_series.pdf` | [murata.com](https://www.murata.com/en-us/products/resistor/highvoltage) |
| Microchip TN0610N3-G | Q1–Q4 | N-MOSFET — opto-LED low-side driver | 100 V, 500 mA, Vgs(th) ≤ 2 V, TO-92 | `TN0610N3-G_Microchip.pdf` | [microchip.com/TN0610](https://www.microchip.com/en-us/product/TN0610) |

## Design notes uncovered while collecting these

1. **R1/R2 value corrected.** Part `MHR0317SA107F70` is **100 MΩ** ("107" = 10×10⁷). The schematic/PCB previously labeled it "50 M" — that label was wrong and has been corrected to "100 M". No part change needed.

2. **OPTO-100 CTR = 0.15% gates the achievable output voltage.** The opto's HV side is a light-controlled photodiode, not a low-impedance switch. Output current Iout ≈ 0.0015 × I_LED. In steady state the channel output settles at V ≈ Iout × R_bleeder (until it nears the 5 kV rail).
   - To reach **5 kV** across a **100 MΩ** bleeder you need Iout ≥ 50 µA → **I_LED ≥ ~33 mA** → opto-LED resistor (R3/R4) ≈ **50–60 Ω**, *not* the present 200 Ω.
   - With the present **200 Ω** (I_LED ≈ 10 mA → Iout ≈ 15 µA) the output is clamped at only **~1.5 kV**. **R3/R4 must be reduced to hit the full voltage** (TBD once final max-V target is set; design is "variable to 5 kV").

3. **SMHV0550 control needs attention:** Program (pin 3) wants a 0–5 V analog level — the Pi has no DAC, so this needs a filtered PWM or an external DAC. Ilimit (pin 7) should be tied to 5 V (disable) or driven 0–1 V. Verify both are wired. Vmon/Imon (0–1 V) can feed an ADC for telemetry.

4. **Input filtering:** the module switches at 45–80 kHz and draws up to ~350 mA pulsed — add input bulk capacitance + an LC/ferrite on its 5 V feed, and budget ~0.5 A total from the Pi 5 V rail (module + 2 opto LEDs + indicators).
