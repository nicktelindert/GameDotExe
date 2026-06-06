#!/bin/bash

# Dit script genereert een macOS .app bundle voor GameDotExe.
# Vereisten: pip install PySide6 requests pyinstaller

APP_NAME="GameDotExe"
MAIN_SCRIPT="main.py"

echo "--- Start macOS Build voor ${APP_NAME} ---"

# Voer PyInstaller uit
# --windowed zorgt voor een .app bundle en voorkomt een terminal venster
# --noconfirm overschrijft oude builds
# --target-arch universal2 probeert een build te maken voor zowel Intel als Apple Silicon
pyinstaller --noconfirm --windowed \
    --name "${APP_NAME}" \
    --add-data "ui:ui" \
    --add-data "assets:assets" \
    --add-data "known_dos_games.json:." \
    --target-arch universal2 \
    "${MAIN_SCRIPT}"

if [ $? -eq 0 ]; then
    echo "--- Ad-hoc signing de bundle ---"
    # Dit helpt om de 'damaged' melding te voorkomen op je eigen systeem
    codesign --force --deep --sign - "dist/${APP_NAME}.app"

    echo "--- Build voltooid! ---"
    echo "De .app bundle staat in de 'dist/' map."
else
    echo "Fout: Build mislukt."
    echo "Tip: Als 'universal2' faalt, zorg dat je 'macholib' hebt geïnstalleerd:"
    echo "pip install macholib"
fi