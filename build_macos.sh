#!/bin/bash

# Dit script genereert een macOS .app bundle voor GameDotExe.
# Vereisten: pip install PySide6 requests pyinstaller

APP_NAME="GameDotExe"
MAIN_SCRIPT="main.py"

echo "--- Start macOS Build voor ${APP_NAME} ---"

# Voer PyInstaller uit
# --windowed zorgt voor een .app bundle en voorkomt een terminal venster
# --noconfirm overschrijft oude builds
pyinstaller --noconfirm --windowed \
    --name "${APP_NAME}" \
    --add-data "assets:assets" \
    --add-data "known_dos_games.json:." \
    "${MAIN_SCRIPT}"

if [ $? -eq 0 ]; then
    echo "--- Build voltooid! ---"
    echo "De .app bundle staat in de 'dist/' map."
else
    echo "Fout: Build mislukt."
fi