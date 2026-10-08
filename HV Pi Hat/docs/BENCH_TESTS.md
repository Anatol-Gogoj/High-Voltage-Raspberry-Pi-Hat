# Bench tests: HV Pi Hat rev B

Measurements the design depends on that no datasheet or drawing settles. Results go in GitHub issue
#7; anything that changes the design goes into an ADR. Work at or below the stated voltages
with a current-limited supply, and discharge HV nodes before touching them.

## Before ordering rev B

### T1. OPTO-100-05 output current vs LED current (ADR-0006)
- Why: the datasheet's CTR graph has a turn-on threshold near 40 mA, its Vin graph does not, and
  rev B's 15 Ohm LED resistors assume the threshold is real.
- Setup: one OPTO-100-05. LED pins 2 (+) and 1 (-) from a current-limited bench supply, 20, 40, 60,
  80, 100, 120, 150 mA (400 mA absolute max). HV leads reverse biased from a low-voltage supply
  (30 to 100 V is enough for photocurrent): RED (cathode) to +, WHITE (anode) to the return through
  a uA meter. Polarity read from the datasheet's application schematic.
- Record: output current at each LED current, and at 0 mA (dark current).
- Pass: at least 50 uA at 110 mA LED current. Record where the output starts to rise.

### T2. OPTO-100-05 HV lead polarity vs the footprint (assembly check)
- Why: a reversed photodiode is forward biased and conducts with no light. The charge opto would
  then hold the DEA at the rail; the discharge opto would short it.
- Check: in the T1 setup, the diode conducts only with RED positive and the LED on. On the board,
  RED goes to the pad at the higher potential: pad 3 of each opto (HV_RAIL for OR1/OR2,
  HV_CHx_DIS for OR3/OR4), WHITE to pad 4 (HV_CHx for OR1/OR2, GND for OR3/OR4). Confirm against
  the footprint's HVIN/HVOUT silkscreen before soldering any opto.

### T3. Raspberry Pi 5 GPIO pin height (ADR-0005)
- Why: the Samtec ESQ-120-14-G-D elevated socket needs at least 3.68 mm of pin engagement, and no
  official drawing gives the Pi 5 header heights.
- Measure with calipers on the bench Pi: h_b = top of the header's plastic base above the Pi PCB,
  h_p = pin tip above the Pi PCB.
- Pass: h_p - h_b >= 3.68 mm.

### T4. Active Cooler height (ADR-0005, informational)
- Measure the highest point of the fitted Active Cooler above the Pi PCB (fan frame and push-pin
  caps). The 20 mm stack assumes 13.70 mm or less.

## On the first article

### T5. Potting qualification (ADR-0003 prerequisite 3)
- Placeholder: DC withstand voltage, duration and partial-discharge limit come from IEC 60664-3
  once the standard is in hand. Run on a potted coupon or the first article.

### T6. SoC temperature with the HAT fitted (ADR-0005)
- The Active Cooler's fan inlet sits about 3.3 mm under the bottom pot.
- 10 min CPU load (e.g. stress-ng) with and without the HAT; log `vcgencmd measure_temp` and
  `vcgencmd get_throttled`.
- Pass: no throttling flags with the HAT fitted.

### T7. STANDBY and boot fail-safe (ADR-0007)
- Put the Pi in STANDBY (EEPROM `POWER_OFF_ON_HALT=1`, then `sudo halt`) with the HAT powered, and
  watch a full boot from cold.
- Pass: the HV rail and both outputs stay at about 0 V throughout (no opto conducts, PGM stays low).

### T8. Bleed-down when unpowered (1 GOhm safety bleeders R25/R26)
- Charge an output with a 1 nF load to about 1 kV, remove all power, record the decay.
- Expected time constant: 1 GOhm x 1 nF = 1 s. An HV probe's own input resistance (often about
  1 GOhm) is in parallel and shortens it; account for it.
- Pass: below 50 V within 10 s.

### T9. Functional
- PGM: HV rail against PWM duty (expect about 4.7 kV at full scale from the build log).
- Charge and discharge time at 1 nF, 0 to 5 kV (ADR-0006 expects about 50 ms per edge).
- Indicator LEDs follow the charge MOSFETs.
- ID EEPROM: program it (ch. 3 of the HAT+ spec), confirm `/proc/device-tree/hat/` shows it.
