# eeschema implementation checklist — control rework + active discharge

Work top-to-bottom in Eeschema. Values/wiring reference `CONTROL_DESIGN.md`.
Don't worry about reference numbers for new parts — place them, then **Tools → Annotate** at the end.
Leave footprint assignment (Phase 7) until the wiring is done.

## Phase 0 — checkpoint
- [ ] Commit current state in git (so we can revert): `git add -A && git commit -m "pre-control-rework"`
- [ ] Open `HV Pi Hat.kicad_sch` in Eeschema.

## Phase 1 — SMHV module (U1) control
- [ ] **ILIMIT:** delete the no-connect on U1 pin 7; wire pin 7 to a **+5V** power symbol.
- [ ] **PGM op-amp stage** (reaches full 5 kV):
  - [ ] Delete the existing wire from GPIO12 to U1 pin 3 (PGM).
  - [ ] Place 1× op-amp `Amplifier_Operational:MCP6001` (single, RRIO). Power V+ = +5V, V− = GND. Add 0.1 µF +5V→GND beside it.
  - [ ] Input filter: GPIO12/PWM0 → **R 10k** → node A. From node A: **C 1µF → GND** and **R 100k → GND** (boot pulldown). Node A → op-amp **+IN**.
  - [ ] Feedback: op-amp **OUT → Rf 5.6k → −IN**, and **Rg 10k from −IN → GND** (gain ≈1.55).
  - [ ] op-amp **OUT → U1 PGM (pin 3)** directly. (optional: 100 nF PGM→GND)
- [ ] **Input power:** add **47 µF + 1 µF + 0.1 µF** (+5V→GND) at U1 VIN; add a **ferrite bead** in the +5V feeding U1.

## Phase 2 — Channel-1 charge drive → parallel (rework existing)
Existing: +5V→R6→D1→R3→OR1 LED→Q1. Make the opto and indicator two parallel branches onto Q1's drain.
- [ ] Delete the wires linking D1 to R3 (break the series chain).
- [ ] **Opto branch:** +5V → **R3 (change 200→51 Ω)** → OR1 LED+ (pin2); OR1 pin1 (LED−) → Q1 DRAIN.
- [ ] **Indicator branch:** +5V → **R6 (change 300→470 Ω)** → D1 (A→K); D1 K → Q1 DRAIN (same node as OR1 pin1).
- [ ] **Gate:** insert **100 Ω** in series in Q1 GATE from its GPIO; add **10k from GATE→GND** (default-off).

## Phase 3 — Channel-1 active discharge (NEW)
- [ ] Place **OR3** = `HV_Electronics:HVM_OR-100` and **Q3** = `HV_Electronics:TN0610N3_G_P013`.
- [ ] **HV path:** DEA node (OR1 HVOUT / J3 pin2) → **R1 (100 MΩ, reused)** → OR3 HVIN (pin3); OR3 HVOUT (pin4) → GND.
  - (R1 currently sits J3pin1→GND — move it to DEA-node → OR3 HVIN.)
- [ ] **Drive:** +5V → **R 51Ω** → OR3 LED+ (pin2); OR3 pin1 → Q3 DRAIN; Q3 SRC → GND; Q3 GATE ← GPIO via **100Ω**, **10k→GND**.

## Phase 4 — Channel-1 output + safety bleeder
- [ ] **J3 pin1 (return) → GND** directly. (J3 pin2 = HV+ / DEA node.)
- [ ] Place **R_safety1** = `MHR0317SA107F70:MHR0317SA107F70`, value **1G**, **mark DNP** (Edit symbol → Do-not-populate). Wire DEA node → R_safety1 → GND.

## Phase 5 — Channel-2 (mirror of 2–4)
- [ ] Charge parallel: +5V→**R4 (200→51)**→OR2 LED; +5V→**R5 (300→470)**→D3; both K/LED− → Q2 DRAIN. Q2 gate 100Ω + 10k pd.
- [ ] Discharge: place **OR4**, **Q4**; DEA node → **R2 (100 MΩ)** → OR4 HVIN; OR4 HVOUT → GND; +5V→51Ω→OR4 LED→Q4; Q4 gate 100Ω+10k pd.
- [ ] **J4 pin1 → GND**; place **R_safety2** 1G (DNP) DEA-node→GND.

## Phase 6 — GPIO assignment (move off ID_SC)
Re-draw these gate/PGM connections to the GPIO header pins:
- [ ] PGM → **GPIO12/PWM0 (pin 32)** (into the op-amp input).
- [ ] Ch1 charge (Q1) → **GPIO5 (pin 29)**   ·  Ch1 discharge (Q3) → **GPIO6 (pin 31)**
- [ ] Ch2 charge (Q2) → **GPIO26 (pin 37)**  ·  Ch2 discharge (Q4) → **GPIO16 (pin 36)**

## Phase 7 — annotate + footprints
- [ ] Tools → **Annotate** (number the new parts).
- [ ] Assign footprints: OR3/OR4 → `HV_Footprints:HVM OR-100`; Q3/Q4 → `TN0610N3_G_P013_Footprint:TO-92_MC_MCH`;
      R_safety → `MHR0317SA107F70:RESRR1524W50L1760T250H500`; op-amp → SOT-23-5; new passives → 0603/0805.
- [ ] (HV output terminals J3/J4 footprint = the 2-pos terminal block — leave as-is for now; we set it during layout.)

## Phase 8 — validate
- [ ] Tools → **ERC**. Resolve dangling wires / unconnected pins (expect a few; fix real ones).
- [ ] Save. Ping me — I'll run the netlist/ERC check, then do **Update PCB from Schematic** + the layout (placement, slots, routing, DRC).
