# HV Output Connector Options — 5 kV DEA-Driver Pi HAT (J3, J4)

**Date:** 2026-06-07
**Board:** 85 x 56 mm 2-channel HAT, output up to 5 kV (run ~4.7 kV max), HV+ and HV- (= board GND/return) per channel, load < 1 nF.
**Distributor preference:** DigiKey, Mouser OK.
**Replaces:** Tyclon **SHV-R** (DigiKey 4912-SHV-R-ND) — rejected: ~34 mm footprint and only **3.5 kV continuous** (5 kV is 1-min withstand only). Interim part is a generic 1x2 screw block.

> **Pricing/stock note:** DigiKey product pages block automated reads (HTTP 403), so unit prices below come from mirror distributors / search snippets and should be confirmed at cart. Stock is approximate as of the date above.

---

## The key engineering point first: this is a *creepage/clearance* problem, not a "buy a 5 kV connector" problem

There is no cheap, small, **truly 5 kV-continuous-rated, board-mount** 2-pin connector. The honest options split three ways:

1. **A coarse-pitch screw terminal** whose geometry gives the creepage (the connector's own *printed* voltage rating is ~1 kV — that number is a UL/IEC pollution-degree-2 spacing rating for the **terminal's own internal** clearances, not a ceiling on what you can run pole-to-pole if you space the poles out and coat the board). The 10.16 mm pitch + large insulating body is what buys the margin.
2. **A genuine HV coax jack** (SHV/MHV). Done "right" (Radiall / Huber+Suhner) these are 5 kV-continuous-plus, but they are panel-mount, ~$25-45, and ~25-34 mm — i.e. the thing you're trying to get away from. Board-mount SHV PCB jacks exist but cap at **3.5 kV continuous**, same trap as the Tyclon.
3. **Directly soldered HV silicone lead + strain relief.** Often the *most* reliable 5 kV termination and the cheapest. No mating connector = no creepage path across a connector body, no contact-resistance hot spots.

**Creepage target (IEC 60664-1):** for ~5 kV working voltage at **pollution degree 2**, required creepage is roughly **9-14 mm** depending on CTI material group; at **pollution degree 1** (achieved by a qualifying conformal coating + sealed enclosure) it drops to roughly **clearance-limited ~5-6 mm**. Your board already runs **4 mm clearance + creepage with conformal coat** on HV nets and a custom DRU. A **10.16 mm-pitch** block gives ~10 mm pole-to-pole creepage on its own — comfortably in range with the coating, and it's the smallest standard pitch that does. **7.62 mm (~7.6 mm creepage) is marginal — only acceptable coated and with a slot/conformal coat;** do not use it bare. Below 7.62 mm: no.

---

## Category 1 — HV-capable 2-position screw terminal blocks (the interim direction, done properly)

The realistic, in-stock, cheap winner. Use **10.16 mm pitch** for genuine 5 kV creepage margin. Both parts below are mainstream, stocked, and have ready KiCad footprints.

| # | Mfr + MPN | DigiKey / Mouser PN | Voltage rating (working) | Mount | Pitch / size | In stock? | ~Price (qty 1) | Pro / Con |
|---|---|---|---|---|---|---|---|---|
| 1A | **Phoenix Contact MKDS 5/2-9,5** (or MKDS 5/ 2-10,16) | DK **277-1248-ND** (9.5 mm) | 1000 V (IEC III/2), 6 kV impulse | THT screw, board | 9.5-10.16 mm, ~17 mm body H | Y, high | ~$2.50 | Pro: rugged, ~9.5-10 mm creepage, trivially sourced. Con: 9.5 mm slightly under ideal — prefer the 10.16 mm sibling. |
| 1B | **Phoenix Contact MKDS 10 HV/ 2-ZB-10,16** (1709681) | DK **277-1685-ND** (verify) | 1000 V (IEC III/2), **6 kV impulse**, CTI 600 (PA body) | THT screw, board | **10.16 mm**, large frame (16 mm² / 76 A) | Y | ~$4-6 | Pro: biggest insulating body + 10.16 mm creepage; "HV" frame, CTI 600 → best geometric margin of the cheap blocks. **KiCad footprint on SnapMagic.** Con: physically tall/bulky (it's really a high-*current* block); overkill conductor size. |
| 1C | **Weidmüller LU 10.16/2** (e.g. 1nnn-series, 2-pole, 10.16 mm) | Mouser 651-/ DK 281-series (verify exact 2-pole 10.16) | 1000 V (IEC), CTI per series | THT screw, board | **10.16 mm** | Y | ~$3-4 | Pro: 10.16 mm pitch, KiCad footprints on SnapMagic. Con: confirm the exact 2-position 10.16 mm orderable PN — Weidmüller's LU naming is dense. |

**What pitch gives real 5 kV margin?** **10.16 mm** (~10 mm creepage) is the sweet spot — first standard pitch that meets ~5 kV PD2 creepage outright, and with your conformal coat (effectively PD1) it has large margin. **12.7 mm** (e.g. MKDS 10 HV/2-12,7) buys even more if board area allows. **7.62 mm** is borderline (coated only). **5.08 mm and below: not for 5 kV.**

> Caveat on the "1000 V" label: that's the connector's rated insulation voltage for its *own* internal geometry under standard pollution. You are not certifying the connector to 5 kV — you are using its **pitch and body as the creepage spacer** between two of your own pads and relying on your board's coating/clearance regime for the rest. This is standard practice for one-off / lab HV gear but is **not** a safety-agency-rated 5 kV termination. For a product you'd want a purpose-built HV connector (Category 2) or potting.

---

## Category 2 — Board/panel-mount HV jacks/receptacles (genuine >= 5 kV rated)

| # | Mfr + MPN | DigiKey / Mouser PN | Voltage rating (working) | Mount | Size | In stock? | ~Price | Pro / Con |
|---|---|---|---|---|---|---|---|---|
| 2A | **Radiall R317580000** (SHV bulkhead recept.) | DK **R317580000** (10521497) | **3.5 kV** operating (mated pair 12 kVDC withstand) | Panel/bulkhead, solder cup | ~25 mm + bayonet | Y, ~368 | ~$31 | Pro: rugged, mated pair 12 kV withstand. Con: **operating spec is 3.5 kV** — same continuous-rating trap as Tyclon; big; pricey; not board-mount. **Not better than the rejected part for *continuous* 5 kV.** |
| 2B | **JAW-DROPPER SVJ-05L** SHV jack, right-angle **PCB mount** | (no DK/Mouser PN — direct/antenna-connector.com) | **3.5 kV rms working**, 5 kV withstand | **PCB, right-angle** | small SHV | Direct order only | n/a (quote) | Pro: actually a *board-mount* SHV (rare). Con: 3.5 kV working again; no DigiKey/Mouser stock; lead time/quote. |
| 2C | **Amphenol RF MHV recept.** (e.g. 000-27000) | DK **000-27000** (2643385) | **5 kV DC** (MHV class) | Panel, solder cup | MHV body | Y | ~$15-25 | Pro: MHV is the 5 kV-class coax std; cheaper than Radiall. Con: panel/solder-cup not board-mount; MHV "5 kV" is a class figure — confirm the specific PN's *continuous* number; recessed-pin MHV is less finger-safe than SHV. |
| 2D | **Huber+Suhner SHV** (11 SHV-50-x series) | Mouser H+S SHV series | SHV class (3.5 kV rms / 5 kV DC typ.) | Panel/bulkhead | SHV | Y (Mouser) | ~$25-40 | Pro: top build quality. Con: still SHV-class continuous limits; panel-mount; pricey. |

**Verdict on Category 2:** none of the *board-mount* HV jacks beat the rejected Tyclon on the thing that mattered (continuous rating) — they're all ~3.5 kV working. The only ones that genuinely exceed 5 kV continuous (Radiall/H+S high-V, true 5 kV MHV) are **panel-mount and as big/expensive as what you rejected.** A smaller-and-cheaper-than-Radiall *and* truly >5 kV board-mount jack **does not appear to exist in DigiKey/Mouser stock today.** If you want a real connector, the right move is a **panel-mount MHV (5 kV) or HV banana wired to the PCB**, not a board jack.

> Standard 4 mm "safety banana" sockets (Stäubli SLB4 etc.) are CAT-rated ~**1 kV** and are **NOT** usable at 5 kV — ruled out.

---

## Category 3 — Wire-to-board HV (often the most reliable 5 kV approach)

| # | Approach | Parts | Voltage | Mount | In stock? | ~Price | Pro / Con |
|---|---|---|---|---|---|---|---|
| 3A | **Direct-solder HV silicone lead + PCB strain relief** | HV silicone wire **5-10 kV** (e.g. 18-20 AWG, 10 kV silicone test-lead wire, DK "silicone wire test leads" partgroup 29052) soldered to a plated HV pad/turret; strain-relieve with a coated zip-tie anchor or potted blob | **5-10 kV** (wire-limited) | Solder to pad/turret | Y (wire is commodity) | ~$1-3/ft + ~$0.30 turret | **Most reliable 5 kV termination.** No mating-connector creepage path, no contact resistance, smallest footprint, cheapest. Con: not field-detachable; needs strain relief + coating; user must solder. |
| 3B | **Keystone HV turret/standoff terminal** (solder post) | Keystone turret terminals (DK Keystone partgroup 23324), e.g. 1502-2 series; or a single large solder pad | post rating high; **creepage set by your spacing** | THT solder post | Y, high | ~$0.20-0.50 | Pro: clean wire anchor, cheap, KiCad footprints exist (TestPoint/Connector libs). Con: bare metal post — must coat/space the two posts >=10 mm apart; not insulated. |
| 3C | **HV silicone lead + ferrule into the interim screw block** | crimp ferrule (e.g. 20-18 AWG insulated ferrule) on 5-10 kV silicone lead, into a 10.16 mm block (1B/1C) | wire 5-10 kV; junction per block geometry | screw block | Y | ~$0.10/ferrule | Pro: keeps a detachable screw interface but with proper HV wire + clean termination. Con: still relies on block geometry for creepage (see Cat 1). |

HV silicone wire is genuinely rated **5, 10, 15 kV+** (stranded tinned Cu, silicone jacket, 200 °C) and is the correct conductor regardless of which termination you pick — **do not run bare hookup wire or standard PVC at 4.7 kV.**

---

## TOP RECOMMENDATION

For this 2-channel, 5 kV, 85 x 56 mm board, ranked:

1. **Primary (lab / current build): Direct-soldered HV silicone lead (Cat 3A) into a plated HV pad with a Keystone turret (Cat 3B) for strain relief.**
   Cheapest, smallest, highest-reliability 5 kV termination; no connector creepage path; matches your existing 4 mm-clearance + conformal-coat HV regime. Use **>=10 kV silicone wire**, anchor + coat the joint, keep the two posts/pads >= 10 mm apart. This is the right answer for a one-off DEA driver.

2. **If you want a re-matable screw interface: Phoenix Contact MKDS 10 HV/ 2-ZB-10,16 (1709681), 10.16 mm pitch (Cat 1B).**
   In-stock, ~$5, ~10 mm pole-to-pole creepage, CTI-600 body, **KiCad footprint available on SnapMagic** (search "MKDS 10 HV/ 2-ZB-10 16"). Terminate the silicone HV lead with a ferrule. This is the proper upgrade from your generic 1x2 block. (MKDS 5/2-9,5 is the smaller fallback if board space is tight, but 9.5 mm is the floor — prefer 10.16 mm.)

3. **Only if a genuine HV *connector* is a hard requirement: panel-mount 5 kV MHV (Amphenol 000-27000, Cat 2C) or Radiall SHV high-V, wired to the PCB — not board-mounted.**
   Accept the size/cost. Do **not** substitute a board-mount SHV PCB jack: every one found tops out at 3.5 kV continuous, i.e. no better than the part you rejected.

### KiCad footprint status
- **MKDS 10 HV/ 2-ZB-10,16** — footprint+symbol on **SnapMagic (SnapEDA)**, KiCad export available. Ready to use.
- **MKDS 5/2-9,5 and Weidmüller LU 10.16/2** — footprints on SnapMagic; also derivable from KiCad's `TerminalBlock_Phoenix` / `TerminalBlock` standard libraries.
- **Direct solder pad + Keystone turret (3A/3B)** — use KiCad `Connector_Pin` / `TestPoint` / `Mounting…` library footprints, or a trivial custom pad. Effectively no custom work.
- **SHV/MHV jacks (Cat 2)** — generally **custom footprint** needed (panel-mount; some on SnapMagic but verify before relying on it).

---

## Sources

- Radiall R317580000 (DigiKey): https://www.digikey.com/en/products/detail/radiall-usa-inc/R317580000/10521497
- Radiall SHV high-voltage connectors: https://www.radiall.com/products/rf-coaxial-connectors/high-voltage-connectors/shv.html
- JAW-DROPPER SVJ-05L SHV PCB-mount jack: https://antenna-connector.com/products/shv-jack-female-right-angle-connector-receptacle-pcb-mount/
- Amphenol RF MHV (000-27000, DigiKey): https://www.digikey.com/en/products/detail/amphenol-rf/000-27000/2643385
- Amphenol RF MHV connectors (5 kV class): https://www.amphenolrf.com/en-us/products/rf-connectors/mhv-connectors/
- Phoenix Contact MKDS 10 HV/ 2-ZB-10,16 (1709681): https://www.phoenixcontact.com/en-us/products/printed-circuit-board-terminal-mkds-10-hv-2-zb-1016-1709681
- Phoenix Contact MKDSP 10N/ 2-10,16 (1000 V, 10.16 mm): https://www.phoenixcontact.com/en-us/products/printed-circuit-board-terminal-mkdsp-10n-2-1016-1773976
- Phoenix Contact MKDS 10 HV footprint (SnapMagic/SnapEDA, KiCad): https://www.snapeda.com/parts/MKDS%2010%20HV/%202-ZB-10%2016/Phoenix%20Contact/view-part/
- Weidmüller terminal-block footprints (SnapEDA): https://www.snapeda.com/parts/1010300000/Weidmuller/view-part/
- Stäubli SLB4 4 mm panel socket (CAT ~1 kV, ruled out): https://www.staubli.com/us/en/electrical-connectors/products/t-m-products/products-for-test-accessories/sockets-2-mm-and-4-mm/panel-mount-socket-slb4-e.html
- HV silicone test-lead wire (DigiKey partgroup): https://www.digikey.com/catalog/en/partgroup/silicone-wire-test-leads/29052
- Genvolt HV silicone cable 10 kV-50 kV: https://www.genvolt.com/product/silicone-cable/
- Keystone turret terminals (DigiKey partgroup): https://www.digikey.com/catalog/en/partgroup/turret-terminals-keystone-electronics/23324
- IEC 60664-1 clearance/creepage calculator: https://tracewidthcalculator.com/clearance-creepage-calculator
- TI "Demystifying Clearance and Creepage for High-Voltage" (SLUP419): https://www.ti.com/lit/pdf/slup419
- Conformal coating effect on creepage (PD2->PD1): https://www.conformalcoating.co.uk/knowledge-hub/technical-articles/conformal-coating-design-hub/conformal-coating-clearance-creepage/
- Tyclon SHV ratings (rejected part, 3.5 kV continuous): https://tyclon.com/pages/shv-rf-coaxial-connectors
