# HV Pi Hat firmware: HAT+ ID EEPROM and Device Tree overlay

Raspberry Pi 5 only. The overlay targets the RP1 GPIO and PWM blocks (`compatible = "brcm,bcm2712"`).

| File | What it is |
|---|---|
| `eeprom/hvdea-hat-eeprom.txt` | `eepmake` settings for U3 (CAT24C32, 0x50): UUID, vendor, product, overlay name |
| `overlay/robotincubator-hvdea-overlay.dts` | Overlay: gate lines held low, GPIO12 muxed to PWM0 channel 0 |
| `scripts/install-overlay.sh` | Installs the overlay and the boot settings below (dry run by default) |
| `scripts/flash-eeprom.sh` | Builds the EEPROM image, writes it, reads it back and compares (dry run by default) |

## GPIO map (from `docs/CONTROL_DESIGN.md`)

| Line | GPIO | Header pin | Active |
|---|---|---|---|
| Ch1 charge | 5 | 29 | high |
| Ch1 discharge | 6 | 31 | high |
| Ch2 charge | 26 | 37 | high |
| Ch2 discharge | 16 | 36 | high |
| HV setpoint (PGM) | 12, PWM0 channel 0 | 32 | duty sets 0 to 5 kV |

Never assert charge and discharge of one channel together: the rail then drains through the
100 MOhm discharge resistor (50 uA at 5 kV, a quarter of the module's 200 uA).

## What the overlay does

1. A pin controller hog on `rp1_gpio` sets GPIO5/6/16/26 to outputs driven low, with the pad
   pull-down on, when the RP1 pin controller probes. The group has no `function`, so it sets pin
   config only and does not claim the pin mux. User space can still request the lines with libgpiod.
2. GPIO12 is muxed to `pwm0` (RP1 function table: GPIO12 = PWM0[0]) with the pad pull-down on, and
   `rp1_pwm0` is enabled. The channel stays disabled until user space enables it through sysfs
   (`/sys/class/pwm/pwmchipN`, where N is the chip whose `device` link ends in `1f00098000.pwm`).
   Run the PWM at 20 kHz or more (RC corner 16 Hz, `docs/CONTROL_DESIGN.md`).

The HAT+ spec (ch. 3) says the firmware "loads the Device Tree overlay named in the EEPROM" from
`/boot/firmware/overlays`, so a programmed EEPROM loads `robotincubator-hvdea.dtbo` on its own.
Names starting `rpi-` are reserved; the spec recommends `manufacturername-hatplusname`.

## Boot settings (`install-overlay.sh`)

- `config.txt`, in a marked `[pi5]` block: `gpio=5,6,12,16,26=op,dl,pd`. The firmware applies
  this before the kernel starts. The Raspberry Pi docs warn of "a delay of a few seconds between
  power being applied and the changes taking effect".
- `cmdline.txt`: `pinctrl_rp1.persist_gpio_outputs=n`. The RP1 pin controller defaults this to
  `true` (`drivers/pinctrl/pinctrl-rp1.c`: "Enable GPIO_OUT persistence when pin is freed"), which
  leaves a gate line driven high if the program holding it exits or crashes. With `n`, a freed
  line returns to input, the 10 kOhm gate pull-down turns the MOSFET off, and the opto stops
  conducting. The control program must therefore hold its lines for as long as it drives them.
- `--dtoverlay` also adds `dtoverlay=robotincubator-hvdea`, for a board whose EEPROM is still blank.
  Do not use it with a programmed EEPROM.

```
sudo apt install device-tree-compiler
sudo sh scripts/install-overlay.sh            # dry run: prints the planned changes
sudo sh scripts/install-overlay.sh --apply    # backups go to <file>.hvdea-bak
```

## Programming the ID EEPROM

Tools: `eepmake`, `eepdump`, `eepflash.sh` from raspberrypi/utils (HAT+ spec appendix B):

```
git clone https://github.com/raspberrypi/utils.git
cd utils/eeptools && cmake . && make && sudo make install
```

Then, with the HAT fitted and the HV outputs unloaded:

```
sudo sh scripts/flash-eeprom.sh            # dry run: builds the image and prints eepdump
sudo sh scripts/flash-eeprom.sh --write    # hold TP1 at GND when asked, release it after
```

U3's WP pin is pulled up by R29 (1 kOhm) to TP1, per HAT+ spec 3.3. Writes only land while TP1
is held low; the script reads the EEPROM back and compares it with the image. After a reboot,
`/proc/device-tree/hat/product` should read `2-Channel DEA High Voltage HAT+`.

The product UUID is fixed per design (spec ch. 3: "A product UUID (required)"). `product_ver`
holds the board revision (0x0002 = rev B); bump it for a new revision.

## Boot window: what holds the HV off before the overlay loads

From power-on until the firmware applies `gpio=` (a few seconds), and again until the kernel
probes RP1, the header pins sit at their power-on pad pulls. The HAT+ spec (2.3) requires a HAT+
to "tolerate weak pull-high or pull-low on any of the GPIO pins at any time". Rev B does not fully
meet that on GPIO12:

| Pad pull-up (assumed; the RP1 datasheet gives no value) | Gate (10 kOhm pull-down) | PGM_IN (R7 10k, R8 100k) | HV rail (x1.55, 1 kV/V) |
|---|---|---|---|
| 33 kOhm | 0.77 V | 2.31 V | 3.6 kV |
| 50 kOhm | 0.55 V | 2.06 V | 3.2 kV |
| 100 kOhm | 0.30 V | 1.57 V | 2.4 kV |

- **GPIO12:** if its pad pulls up during the window, R8 (100 kOhm) loses to the pull-up and the
  module is programmed to roughly 2.4 to 3.6 kV. A pad pull-down keeps PGM at 0 V. RP1's reset
  pull state is "varies" per pin in the RP1 datasheet (PADS_BANK0 PUE/PDE), so measure it (T7).
- **GPIO5/6/16/26:** with a pad pull-up the gate sits near the TN0610's 0.6 V minimum threshold
  (datasheet: VGS(th) 0.6 to 2.0 V at 1 mA). The drain current there is milliamps at most, far
  below the about 40 mA where the OPTO-100 starts to conduct (ADR-0006), so the optos stay off.
- The optos are then the only barrier between a live rail and the outputs during the window.
  Firmware cannot close it; a stronger GPIO12 pull-down or an HV-enable gate needs a hardware
  change (issue #10 recommends a 1 kOhm pull-down on GPIO12).
