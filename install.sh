#!/bin/bash
set -e

REPO_URL="https://github.com/timi2506/MyPayIndia-HA.git"
DOMAIN="mypayindia"
TEMP_DIR="/tmp/mypayindia_repo"

if [ -d "/config" ]; then
    HASS_CONFIG="/config"
elif [ -d "$HOME/.homeassistant" ]; then
    HASS_CONFIG="$HOME/.homeassistant"
else
    echo "Could not find Home Assistant configuration directory."
    exit 1
fi

TARGET_DIR="$HASS_CONFIG/custom_components/$DOMAIN"

rm -rf "$TEMP_DIR"
git clone --depth 1 "$REPO_URL" "$TEMP_DIR"

mkdir -p "$HASS_CONFIG/custom_components"

if [ -d "$TARGET_DIR" ]; then
    rm -rf "$TARGET_DIR"
fi

cp -r "$TEMP_DIR/custom_components/$DOMAIN" "$HASS_CONFIG/custom_components/"
rm -rf "$TEMP_DIR"

echo ""
echo "Installation successful!"
echo "------------------------------------------------------"
echo "IMPORTANT: You must RESTART Home Assistant now."
echo "------------------------------------------------------"
