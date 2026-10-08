# High Voltage Raspberry Pi Hat
A high voltage Raspberry Pi hat dedicated to controlling and powering Dielectric Elastomer Actuators (DEAs) through a dedicated circuit without the risk of burning out expensive high voltage equipment.

Two channels, up to 5 kV into loads under 1 nF, with independent charge, hold and active
discharge per channel and a passive 1 GOhm bleeder across each output. Rev B fits the standard
65 x 56.5 mm HAT+ outline with the HV section potted. KiCad 10 project in
[`HV Pi Hat/`](HV%20Pi%20Hat/); design decisions are in
[`HV Pi Hat/docs/adr/`](HV%20Pi%20Hat/docs/adr/).

**Safety:** this board generates 5 kV. It has not been fabricated or reviewed by a qualified
electrical engineer, and the HV spacing basis is still open (ADR-0003). Do not build or energize
it from this repository as it stands.
