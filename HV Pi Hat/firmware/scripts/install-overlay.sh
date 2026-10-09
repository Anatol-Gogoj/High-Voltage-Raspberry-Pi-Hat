#!/bin/sh
# install-overlay.sh - install the HV Pi Hat Device Tree overlay and boot settings on a Raspberry Pi 5.
#
# Changes, each backed up to <file>.hvdea-bak before the first edit:
#  1. /boot/firmware/overlays/robotincubator-hvdea.dtbo   compiled from overlay/*.dts (needs dtc)
#  2. /boot/firmware/config.txt   a marked [pi5] block: gpio= lines that drive the gate and PGM lines
#                                 low from early firmware boot, before the kernel loads the overlay.
#                                 With --dtoverlay (blank or unprogrammed EEPROM only) it also adds
#                                 dtoverlay=robotincubator-hvdea; a programmed EEPROM loads it already.
#  3. /boot/firmware/cmdline.txt  pinctrl_rp1.persist_gpio_outputs=n, so a gate line returns to input
#                                 (pulled low, MOSFET off) when the program holding it exits or crashes.
#                                 The default (y) leaves the last driven level on the pin.
#
# Usage: sudo sh install-overlay.sh                  (show the planned changes, change nothing)
#        sudo sh install-overlay.sh --apply [--dtoverlay]
set -eu

Here=$(cd "$(dirname "$0")" && pwd)
Dts="$Here/../overlay/robotincubator-hvdea-overlay.dts"
Boot=${HVDEA_BOOT:-/boot/firmware}          # override for testing only
Compat=${HVDEA_COMPAT:-/proc/device-tree/compatible}
Dtbo="$Boot/overlays/robotincubator-hvdea.dtbo"
Config="$Boot/config.txt"
Cmdline="$Boot/cmdline.txt"
Begin="# >>> HV Pi Hat (robotincubator-hvdea) >>>"
End="# <<< HV Pi Hat (robotincubator-hvdea) <<<"
Param="pinctrl_rp1.persist_gpio_outputs=n"

Apply=0
AddDtoverlay=0
for Arg in "$@"; do
	case "$Arg" in
		--apply) Apply=1 ;;
		--dtoverlay) AddDtoverlay=1 ;;
		*) echo "Unknown option: $Arg" >&2; exit 1 ;;
	esac
done

if ! grep -q "bcm2712" "$Compat" 2>/dev/null; then
	echo "This is not a Raspberry Pi 5 (bcm2712). Stopping." >&2
	exit 1
fi
for File in "$Config" "$Cmdline"; do
	[ -f "$File" ] || { echo "Not found: $File" >&2; exit 1; }
done
if ! command -v dtc >/dev/null 2>&1; then
	echo "dtc not found: sudo apt install device-tree-compiler" >&2
	exit 1
fi

Block=$(mktemp)
trap 'rm -f "$Block"' EXIT
{
	echo "$Begin"
	echo "[pi5]"
	echo "# Gate lines (GPIO5/6/16/26) and HV setpoint (GPIO12): outputs, driven low, pad pull-down"
	echo "gpio=5,6,12,16,26=op,dl,pd"
	[ "$AddDtoverlay" -eq 1 ] && echo "dtoverlay=robotincubator-hvdea"
	echo "[all]"
	echo "$End"
} > "$Block"

echo "Planned changes:"
echo "  $Dtbo  <- dtc $Dts"
if grep -qF "$Begin" "$Config"; then
	echo "  $Config: replace the existing HV Pi Hat block with:"
else
	echo "  $Config: append:"
fi
sed 's/^/      /' "$Block"
if grep -qF "$Param" "$Cmdline"; then
	echo "  $Cmdline: already has $Param"
else
	echo "  $Cmdline: append $Param"
fi

if [ "$Apply" -ne 1 ]; then
	echo
	echo "Dry run: nothing changed. Re-run with --apply."
	exit 0
fi
if [ "$(id -u)" != "0" ]; then
	echo "Applying needs root: sudo sh $0 --apply" >&2
	exit 1
fi

Backup() {
	[ -f "$1" ] && [ ! -f "$1.hvdea-bak" ] && cp -p "$1" "$1.hvdea-bak"
	return 0
}

# 1. Overlay
Backup "$Dtbo"
dtc -@ -q -I dts -O dtb -o "$Dtbo.new" "$Dts"
mv "$Dtbo.new" "$Dtbo"

# 2. config.txt: drop any old block between the markers, then append the new one
Backup "$Config"
awk -v B="$Begin" -v E="$End" '$0 == B {Skip = 1} !Skip {print} $0 == E {Skip = 0}' "$Config" > "$Config.new"
cat "$Block" >> "$Config.new"
mv "$Config.new" "$Config"

# 3. cmdline.txt is a single line; append the parameter to it
if ! grep -qF "$Param" "$Cmdline"; then
	Backup "$Cmdline"
	Line=$(head -n 1 "$Cmdline")
	printf '%s %s\n' "$Line" "$Param" > "$Cmdline.new"
	mv "$Cmdline.new" "$Cmdline"
fi

sync
echo "Done. Backups: *.hvdea-bak next to each changed file. Reboot to take effect."
