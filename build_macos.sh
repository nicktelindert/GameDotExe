#!/bin/bash

# Dit script genereert een macOS .app bundle voor GameDotExe.
# Vereisten: pip install PySide6 requests pyinstaller

APP_NAME="GameDotExe"
MAIN_SCRIPT="main.py"

echo "--- Start macOS Build voor ${APP_NAME} ---"

# Voer PyInstaller uit
# Optimalisaties:
# 1. --exclude-module: Voorkom dat zware, ongebruikte Qt modules worden meegeleverd.
# 2. Architectuur: 'universal2' is handig maar zwaar. Overweeg je eigen architectuur voor een lichtere build.
pyinstaller --noconfirm --windowed \
    --name "${APP_NAME}" \
    --exclude-module PySide6.QtWebEngineCore \
    --exclude-module PySide6.QtWebEngineWidgets \
    --exclude-module PySide6.QtDesigner \
    --exclude-module PySide6.Qt3DCore \
    --exclude-module PySide6.QtCharts \
    --exclude-module PySide6.QtSql \
    --exclude-module PySide6.QtTest \
    --exclude-module PySide6.QtMultimedia \
    --exclude-module PySide6.QtBluetooth \
    --exclude-module PySide6.QtPositioning \
    --exclude-module tkinter \
    --exclude-module unittest \
    --add-data "ui:ui" \
    --add-data "assets:assets" \
    --add-data "core/known_dos_games.json:core" \
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