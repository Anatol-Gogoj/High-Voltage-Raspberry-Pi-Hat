# Sourced Bill of Materials — 5 kV HV Raspberry Pi HAT (DEA driver)

**Date sourced:** 2026-06-07
**Distributors:** DigiKey preferred, Mouser/LCSC as fallback.
**Verification:** Specialty/high-risk parts (HVM modules, SHV connector, 1 GΩ HV resistor, TN0610 MOSFET) verified via live web lookups. Commodity passives use representative in-stock DigiKey catalog parts per value.

> **Pricing note:** DigiKey's product pages block automated reads (HTTP 403), so unit prices marked "~" were obtained from search snippets / mirror distributors and should be confirmed at checkout. Stock figures are approximate as of the date above.

---

## BOM Table

| Ref(s) | Qty | Value/Part | Package | Manufacturer + MPN | DigiKey/Mouser PN | In stock? (Y/N + approx qty) | Unit price | Notes |
|---|---|---|---|---|---|---|---|---|
| U1 | 1 | SMHV0550 — 5 kV / 200 µA programmable HV DC-DC | Module 0.85"x0.85"x0.6" | HVM Technology SMHV0550 | DigiKey **2244-SMHV0550-ND** (base), product 10708015 | Y — stocked catalog item ("ships today"); typically low/MOQ-of-1 qty, confirm at cart | ~$200–300 (confirm) | **Catalog item on DigiKey — no RFQ needed.** Output proportional to 0–5 V program input. 5 V ±10% supply. Also orderable direct from hvmtech.com (RFQ, tel 830-626-5552). The "-S2" suffix is a packaging/variant; the bare **SMHV0550** matches the schematic symbol. |
| OR1–OR4 | 4 | OPTO-100-05 — 10 kV HV opto-coupler | Epoxy body 0.40"L x 0.24"W x 0.25"H (10.2 x 6.1 x 6.4 mm), LED pins 0.350" apart, HV on flying wire leads (datasheet Rev B, p. 2) | HVM Technology OPTO-100-05 | DigiKey **2244-OPTO-100-05-ND**, product 16378579 | Y — stocked catalog item ("ships today") | ~$94.74 DK (≈$74 at LCSC C17566441) | **Catalog item on DigiKey — orderable, not RFQ-only.** 10 kV reverse-voltage rating, internal current-limit R, no external parts. LED Vf = 3.25 V @ 100 mA. **4 needed = ~$380 — largest BOM cost driver after U1.** |
| U2 | 1 | MCP6001 op-amp, 1 MHz RRIO | SOT-23-5 ("OT") | Microchip MCP6001T-I/OT | DigiKey **MCP6001T-I/OTCT-ND** (cut tape), product 551760 | Y — high stock (mainstream part) | ~$0.42 | "OT" = SOT-23-5 per schematic (symbol MCP6001-OT). I-grade (-40…+85 °C). |
| Q1–Q4 | 4 | N-MOSFET, 100 V, logic-level | TO-92 | Microchip (Supertex) TN0610N3-G | DigiKey **TN0610N3-G-ND**, product 4902374 | Y — **active, ships today** | ~$0.70 | 100 V Vds, 500 mA, Vgs(th) typ ~1.5 V (logic-level), 1 W. Confirmed NOT EOL. Schematic uses the **-P013** ammo/tape variant (DigiKey **TN0610N3-G-P013** / Mouser 579-TN0610N3-G-P013) — order whichever pack form you prefer; die is identical. See alternatives note below. |
| R1, R2 | 2 | 100 MΩ HV resistor, 1%, 7 kV | Axial 0317 (lead pitch 15.24 mm) | Murata MHR0317SA107F70 | DigiKey **MHR0317SA107F70-ND** (verify current DK#); confirmed catalog part | Y — ~4,155 (mirror); on DigiKey catalog | ~$1.10 (qty1), ~$0.37 @1k | 100 MΩ confirmed (107 = 100 MΩ). 0.8 W. Matches schematic symbol/footprint exactly. |
| R25, R26 | 2 | 1 GΩ HV resistor, 1%, 7 kV (populated by default as the fail-safe bleeder; DNP-able) | Axial 0317 (lead pitch 15.24 mm) | Murata MHR0317SA108F70 | DigiKey product **9950895** (DK# MHR0317SA108F70-ND) | **Partial** — real Murata catalog part with live DigiKey page; one mirror showed 0 stock, so **verify live stock before ordering** | ~$1.10 (qty1) | **CONFIRMED this 1 GΩ part exists** in the same 0317 series (108 = 1000 MΩ). 7 kV rated, 0.8 W. Populated by default (fail-safe bleed-down), so stock matters: verify before ordering. Fallback if DK out: Ohmite "Slim-Mox"/Vishay VR37 GΩ-range HV axials (≥5 kV), or Vishay VHV/RNX. |
| J3, J4 | 2 | Soldered HV lead pair per channel (pad 1 return/GND, pad 2 HV), potted in place (ADR-0003) | THT, footprint `HV_Footprints:HV_LeadPair_P6.00mm` (2.4 mm pads, 1.2 mm drill, 6.0 mm pitch) | Wire: HV silicone, 10 kV or higher rated, 18 to 20 AWG (part not yet chosen) | See `docs/HV_CONNECTOR_OPTIONS.md` | n/a | n/a | Rev B replaced the 10.16 mm screw terminals: a terminal cannot sit inside the pot. Ranked first in the connector study. |
| GPIO1 | 1 | 2x20 (40-pin) 2.54 mm female header | THT, dual row | Sullins PPTC202LFBN-RC | DigiKey **S6104-ND**, product 807240 | Y — high stock | ~$1.10 | Plain 2x20 female socket (non-stacking). For a stacking/extended HAT header use Samtec SSQ-120-03-T-D or Sullins PPPC202LFBN-RC (S7123-ND). |
| D1, D2 | 2 | LED indicator, ~2 V | 0603 | Würth 150060GS75000 (green) | DigiKey **732-4971-1-ND** | Y — very high stock | ~$0.12 | Any 0603 LED is fine; green Vf ~2.0 V. Pair with appropriate series R (see 470 Ω / 1 k). |
| FB1 | 1 | Ferrite bead, 600 Ω @ 100 MHz, ≥0.5 A | 0805 | Murata BLM21AG601SN1D | DigiKey **490-1054-1-ND**, product 584251 | Y — very high stock | ~$0.10 | 600 Ω @100 MHz, 600 mA. For higher current use BLM21SP601SH1D (2.3 A, power line). |
| C2 | 1 | 47 µF, ≥10 V, X5R/X7R MLCC | 1206 | Murata GRM31CR61A476KE15L (47 µF 10 V X5R) | DigiKey **490-5523-1-ND** | Y — high stock | ~$0.30 | 1206, 10 V X5R. For more margin use 16 V (GRM31CR61C476K). |
| C1, C3 | 2 | 1 µF, ≥16 V MLCC | 0603 | Murata GRM188R61E105KA12D (1 µF 25 V X5R) | DigiKey **490-5523-2-... / 490-1543-1-ND** | Y — very high stock | ~$0.10 | 0603, 25 V X5R (>16 V margin). |
| C4, C5 | 2 | 0.1 µF, ≥16 V MLCC | 0603 | Murata GRM188R71H104KA93D (0.1 µF 50 V X7R) | DigiKey **490-3553-1-ND** | Y — very high stock | ~$0.10 | 0603, 50 V X7R. |
| R6, R14, R21, R22 | 4 | 51 Ω, 1%, 0.1 W | 0603 | Yageo RC0603FR-0751RL | DigiKey **311-51.0HRCT-ND** | Y — very high stock | ~$0.10 | 0603 0.1 W ≥ the ~0.09 W load. |
| R11, R15 | 2 | 470 Ω, 1% | 0603 | Yageo RC0603FR-07470RL | DigiKey **311-470HRCT-ND** | Y — very high stock | ~$0.10 | LED series resistors (with D1/D2). |
| R16, R17, R18, R23 | 4 | 100 Ω, 1% | 0603 | Yageo RC0603FR-07100RL | DigiKey **311-100HRCT-ND** | Y — very high stock | ~$0.10 | |
| R7, R10, R13, R19, R20, R24 | 6 | 10 kΩ, 1% | 0603 | Yageo RC0603FR-0710KL | DigiKey **311-10.0KHRCT-ND** | Y — very high stock | ~$0.10 | |
| R8 | 1 | 100 kΩ, 1% | 0603 | Yageo RC0603FR-07100KL | DigiKey **311-100KHRCT-ND** | Y — very high stock | ~$0.10 | |
| R9 | 1 | 5.6 kΩ, 1% | 0603 | Yageo RC0603FR-075K6L | DigiKey **311-5.60KHRCT-ND** | Y — very high stock | ~$0.10 | |

---

## SOURCING RISKS (needs user attention)

1. **SHV connector (J3, J4) — RESOLVED 2026-06-07 → now a 1×2 screw terminal.**
   > **UPDATE:** J3/J4 are no longer SHV. Per the user decision they are now a generic **1×2 screw
   > terminal, 10.16 mm pitch** (`TerminalBlock_RND_205-00241`, pitch-compatible with **Phoenix MKDS
   > 10 HV / 1709681**); see the dedicated study `docs/HV_CONNECTOR_OPTIONS.md`. **Correction to the
   > note below:** the Radiall **R317580000 operating rating is ~3.5 kV** (its 12 kV is only mated-pair
   > *withstand*), so it does **not** solve the continuous-rating problem either; no board-mount SHV
   > jack exceeds 3.5 kV continuous. The genuinely-safe 5 kV options are panel-mount MHV/Radiall
   > (operating-rated) or a **direct-soldered HV silicone lead** (best). Original SHV note kept below.

1b. **(superseded) Original SHV note.**
   - The schematic footprint is named `4912-SHV-R-ND`, which mixes two unrelated parts: **Keystone 4912** is a 0.25" quick-fit *terminal* (not SHV), while **SHV-R** is the **Tyclon** SHV jack. The actual orderable SHV jack is **Tyclon SHV-R** (DigiKey marketplace 19092455, ~$12.08, ~929 in stock).
   - **Problem:** the Tyclon SHV line is rated **3.5 kV continuous, 5 kV withstand for 1 minute only.** Running it at 5 kV *continuous* gives essentially zero margin and is outside its continuous rating.
   - **Recommended fix:** use **Radiall R317580000** (DigiKey, ~$29.60; mated pair rated **12 kVDC**) for real ≥5 kV margin. Caveat: it is a panel-mount **bulkhead/solder-cup** SHV receptacle, not a board-mount PCB jack — you'd mount it to the enclosure and wire to the PCB (good HV practice anyway). Distributor listings disagree on male/female and "plug vs receptacle," so **confirm gender/mate against your cable before ordering.** Verify final DigiKey PN at checkout.
   - Action: decide enclosure-mount (Radiall, recommended for 5 kV) vs. board-mount (Tyclon, only acceptable if actual operating voltage stays well under 3.5 kV).

2. **U1 SMHV0550 (5 kV DC-DC module) — specialty, but stocked.**
   - Good news: it IS a DigiKey catalog item (product 10708015, "ships today"), so **no RFQ is strictly required.** Also available direct from hvmtech.com. Expect ~$200–300/unit; confirm exact price + live stock at cart (DigiKey blocks automated price scraping). If DigiKey shows 0, lead time direct from HVM can be multiple weeks.

3. **OR1–OR4 OPTO-100-05 (10 kV opto) — specialty, stocked, and the dominant passive cost.**
   - Catalog item on DigiKey (product 16378579), ~$94.74 each → **~$380 for the 4 needed.** Cheaper at LCSC (~$74, C17566441) if you can use that channel. Confirm live stock; if short, HVM direct or Luso Electronics (UK) carry it.

4. **R25/R26 1 GΩ HV resistor (MHR0317SA108F70) — confirmed real, but verify live stock.**
   - The 1 GΩ / 7 kV / 0317 part exists with a live DigiKey page (product 9950895). One mirror distributor showed 0 stock, so **check DigiKey stock before relying on it.** Because these are DNP/optional, this is low-impact. Fallback ≥5 kV 1 GΩ axials: Ohmite Slim-Mox, Vishay VR37, or Caddock MX/MG series.

5. **TN0610N3-G (Q1–Q4) — verified ACTIVE, low risk.**
   - Confirmed in stock and not EOL (DigiKey 4902374, "ships today"; also Mouser, RS, TME). Schematic specifies the **-P013** ammo-pack variant — same die, just packaging. If you ever need a second source, pin/spec-compatible TO-92 logic-level N-MOSFETs ≥100 V: **Diodes/Zetex ZVN4310A** (100 V, Vgs(th) ≤2.5 V) or **BSS127S-class** (note SOT-23, not TO-92). For exact TO-92 footprint, Microchip **TN0702N3-G** (200 V sibling) is the closest family alternative.

---

## Source links

- SMHV0550 (DigiKey): https://www.digikey.com/en/products/detail/hvm-technology-inc/SMHV0550/10708015
- SMHV series (HVM): https://www.hvmtech.com/smhv-series
- OPTO-100-05 (DigiKey): https://www.digikey.com/en/products/detail/hvm-technology-inc/OPTO-100-05/16378579
- OPTO-100-05 (HVM): https://www.hvmtech.com/opto100
- OPTO-100-05 (LCSC): https://www.lcsc.com/product-detail/C17566441.html
- MHR0317SA107F70 (Murata/DigiKey via mirror): https://www.xonelec.com/mpn/murata/mhr0317sa107f70
- MHR0317SA108F70 (DigiKey): https://www.digikey.com/en/products/detail/murata-power-solutions-inc/MHR0317SA108F70/9950895
- Tyclon SHV-R (DigiKey): https://www.digikey.com/en/products/detail/tyclon/SHV-R/19092455
- Tyclon SHV voltage ratings: https://tyclon.com/pages/shv-rf-coaxial-connectors
- Radiall R317580000 (DigiKey): https://www.digikey.com/en/products/detail/radiall-usa-inc/R317580000/10521497
- MCP6001T-I/OT (DigiKey): https://www.digikey.com/en/products/detail/microchip-technology/MCP6001T-I-OT/551760
- TN0610N3-G (DigiKey): https://www.digikey.com/en/products/detail/microchip-technology/TN0610N3-G/4902374
- Sullins PPTC202LFBN-RC (DigiKey): https://www.digikey.com/en/products/detail/sullins-connector-solutions/PPTC202LFBN-RC/807240
- BLM21AG601SN1D ferrite (DigiKey): https://www.digikey.com/en/products/detail/murata-electronics/BLM21AG601SN1D/584251
