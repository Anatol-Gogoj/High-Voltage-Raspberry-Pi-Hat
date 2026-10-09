#!/bin/sh
# flash-eeprom.sh - build the HAT+ ID EEPROM image and write it to U3 (CAT24C32, I2C 0x50).
# Run on the Raspberry Pi 5 with the HV Pi Hat fitted and the HV outputs unloaded.
#
# Needs eepmake, eepdump and eepflash.sh from raspberrypi/utils (eeptools), see firmware/README.md.
# Write protect: U3 WP is pulled up by R29 (1 kOhm). Hold test point TP1 at GND for the whole write,
# then release it. With TP1 released the write fails and the read-back check below reports it.
#
# Usage: sudo sh flash-eeprom.sh            (show what would happen, write nothing)
#        sudo sh flash-eeprom.sh --write    (build, write, read back, compare)
set -eu

Here=$(cd "$(dirname "$0")" && pwd)
Settings="$Here/../eeprom/hvdea-hat-eeprom.txt"
Work=$(mktemp -d)
Image="$Work/hvdea-hat.eep"
ReadBack="$Work/readback.eep"
trap 'rm -rf "$Work"' EXIT
Compat=${HVDEA_COMPAT:-/proc/device-tree/compatible}   # override for testing only

Write=0
[ "${1:-}" = "--write" ] && Write=1

for Tool in eepmake eepdump eepflash.sh; do
	if ! command -v "$Tool" >/dev/null 2>&1; then
		echo "Missing $Tool. Build and install raspberrypi/utils eeptools first (firmware/README.md)." >&2
		exit 1
	fi
done
if ! grep -q "bcm2712" "$Compat" 2>/dev/null; then
	echo "This is not a Raspberry Pi 5 (bcm2712). Stopping." >&2
	exit 1
fi

eepmake "$Settings" "$Image"
Size=$(wc -c < "$Image")
echo "Built $Image ($Size bytes) from $Settings:"
eepdump "$Image" "$Work/dump.txt" >/dev/null
cat "$Work/dump.txt"

if [ "$Write" -ne 1 ]; then
	echo
	echo "Dry run: nothing written. Re-run with --write to program U3 at 0x50."
	exit 0
fi
if [ "$(id -u)" != "0" ]; then
	echo "Writing needs root: sudo sh $0 --write" >&2
	exit 1
fi

echo
echo "Hold TP1 at GND now (EEPROM write enable) and keep it there until the read-back finishes."
printf 'Type yes when TP1 is held low: '
read -r Answer
[ "$Answer" = "yes" ] || { echo "Stopped."; exit 1; }

eepflash.sh -w -y -t=24c32 -a=50 -f="$Image"
eepflash.sh -r -y -t=24c32 -a=50 -f="$ReadBack"

if cmp -n "$Size" "$Image" "$ReadBack"; then
	echo "Read-back matches the image ($Size bytes). Release TP1."
	echo "Reboot, then check: cat /proc/device-tree/hat/product /proc/device-tree/hat/vendor"
else
	echo "Read-back does NOT match. Was TP1 held at GND during the write?" >&2
	exit 1
fi
