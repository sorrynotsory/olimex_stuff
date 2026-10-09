#!/usr/bin/env bash
#
# This script will force 1920x1080 resolution!
# ! If resolution is other than defailt 1024x768 it will stop !
# If you want to force other resolution change line 47 : /lib/firmware/edid/1920x1080.bin to what you need
# Can be run with argument "-reboot y" or "-reboot n"
# Skip the prompt and reboot immediately: ./fix_hdmi_resolution.sh -reboot y
# Skip the prompt and completely cancel the reboot: ./fix_hdmi_resolution.sh -reboot n
# Run interactively (asks you manually if no flag is provided): ./fix_hdmi_resolution.sh

# Exit immediately if a command exits with a non-zero status
set -e
# Initialize variables with defaults
REBOOT_CHOICE=""

# 1. Check current resolution
if [ -f /sys/class/graphics/fb0/virtual_size ]; then
    CURRENT_RES=$(cat /sys/class/graphics/fb0/virtual_size)
    if [ "$CURRENT_RES" = "1024,768" ]; then
        echo "Resolution is 1024,768. Proceeding with the script..."
    else
        echo "Resolution is $CURRENT_RES (not 1024,768). Stopping."
        exit 0
    fi
else
    echo "Error: /sys/class/graphics/fb0/virtual_size not found. Stopping."
    exit 1
fi

# Ensure the script is run as root for the following steps
if [ "$EUID" -ne 0 ]; then
    echo "Please run this script as root (sudo)."
    exit 1
fi

# 2. Create the initramfs hook
echo "Creating initramfs hook..."
cat << 'EOF' > "/etc/initramfs-tools/hooks/edid"
#!/bin/sh
PREREQ=""
prereqs() {
    echo "$PREREQ"
}
case $1 in
prereqs)
    prereqs
    exit 0
    ;;
esac
. /usr/share/initramfs-tools/hook-functions
mkdir -p "${DESTDIR}/lib/firmware/edid"
cp /lib/firmware/edid/1920x1080.bin "${DESTDIR}/lib/firmware/edid/"
EOF

# 3. Make hook executable
echo "Setting executable permissions on hook..."
chmod +x /etc/initramfs-tools/hooks/edid

# 4. Update initramfs
echo "Updating initramfs..."
update-initramfs -u -k $(uname -r)

# 5. Create uInitrd image
echo "Creating mkimage ramdisk..."
mkimage -A arm -O linux -T ramdisk -C gzip -d /boot/initrd.img-$(uname -r) /boot/uInitrd

# 6. Modify /boot/boot.cmd
BOOT_CMD="/boot/boot.cmd"
if [ -f "$BOOT_CMD" ]; then
    echo "Modifying $BOOT_CMD..."
    # Backup the original file just in case
    cp "$BOOT_CMD" "${BOOT_CMD}.bak"
    # 1. Update sunxi_fb_mem_reserve
    sed -i 's/sunxi_fb_mem_reserve=16/sunxi_fb_mem_reserve=64/g' "$BOOT_CMD"
    # 2. Insert video arguments inside the closing quote of bootargs
    if grep -q 'setenv bootargs ".*"' "$BOOT_CMD"; then
        # If bootargs is wrapped in double quotes, insert right before the closing quote
        sed -i '/setenv bootargs/s/"$/ video=HDMI-A-1:1920x1080@60D drm.edid_firmware=HDMI-A-1:edid\/1920x1080.bin"/' "$BOOT_CMD"
    else
        # If there are no quotes, append to the end of the line safely
        sed -i '/setenv bootargs/s/$/ video=HDMI-A-1:1920x1080@60D drm.edid_firmware=HDMI-A-1:edid\/1920x1080.bin/' "$BOOT_CMD"
    fi
else
    echo "Error: $BOOT_CMD not found!"
    exit 1
fi

# 7. Compile boot.cmd into boot.scr
echo "Compiling boot script..."
mkimage -C none -A arm -T script -d /boot/boot.cmd /boot/boot.scr

# 8. Reboot
echo "Changes have been successfully applied."
# Prompt the user for a reboot

# Parse command line arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        -reboot)
            if [[ -n "$2" && ! "$2" =~ ^- ]]; then
                REBOOT_CHOICE="$2"
                shift 2
            else
                echo "Error: -reboot requires an argument (y/n)." >&2
                exit 1
            fi
            ;;
        *)
            echo "Unknown argument: $1" >&2
            exit 1
            ;;
    esac
done

# --- Your script changes would go here ---
echo "Changes have been successfully applied."
# ----------------------------------------

# Normalize choice to lowercase if it was passed via argument
REBOOT_CHOICE=$(echo "$REBOOT_CHOICE" | tr '[:upper:]' '[:lower:]')

# If no argument was provided, ask interactively
if [[ -z "$REBOOT_CHOICE" ]]; then
    read -p "Do you want to reboot now to apply all system changes? (y/N): " response
	# Convert the response to lowercase
    REBOOT_CHOICE=$(echo "$response" | tr '[:upper:]' '[:lower:]')
fi

# Execute based on the choice
case "$REBOOT_CHOICE" in
    [yY][eE][sS]|[yY])
        echo "Rebooting the system now..."
        sudo reboot
        ;;
    no|n|*)
        echo "Reboot canceled. Please remember to reboot later to apply changes."
        exit 0
        ;;
	*)
        echo "Reboot canceled. Please remember to reboot later to apply changes."
        exit 0
        ;;
esac
