#!/bin/bash

# Dit script genereert een AppImage voor GameDotExe.
# Vereisten:
# - Python 3.8+
# - pip install PySide6 requests pyinstaller
# - appimagetool (van https://github.com/probonopd/go-appimage)
#   Zorg dat 'appimagetool' in je PATH staat.

APP_NAME="GameDotExe"
MAIN_SCRIPT="main.py"
DIST_DIR="dist"
APPDIR_PATH="${DIST_DIR}/${APP_NAME}.AppDir"

echo "--- Start AppImage generatie voor ${APP_NAME} ---"

# 1. Controleer of PyInstaller is geïnstalleerd
if ! command -v pyinstaller &> /dev/null
then
    echo "PyInstaller is niet gevonden. Installeer het met: pip install pyinstaller"
    exit 1
fi

# 2. Controleer of appimagetool aanwezig is
APPIMAGETOOL_PATH=$(command -v appimagetool)
if [ -z "$APPIMAGETOOL_PATH" ]; then
    echo "appimagetool is niet gevonden."
    echo "Download het van https://github.com/probonopd/go-appimage/releases"
    echo "en voeg het toe aan je PATH."
    exit 1
fi

# 3. Zoek het pad naar de lokale dosbox binary om te bundelen
DOSBOX_BIN=$(command -v dosbox)
if [ -z "$DOSBOX_BIN" ]; then
    echo "Waarschuwing: dosbox binary niet gevonden op dit systeem."
    echo "Installeer dosbox (bijv. sudo apt install dosbox) om het mee te bundelen."
fi

echo "--- Stap 1: Bundelen met PyInstaller ---"
# We voegen de data bestanden direct toe aan de PyInstaller bundle
pyinstaller --noconfirm --onefile --windowed \
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
    --add-data "assets:assets" \
    ${DOSBOX_BIN:+--add-binary "$DOSBOX_BIN:."} \
    --add-data "ui:ui" \
    --add-data "core/known_dos_games.json:core" \
    --name "${APP_NAME}" "${MAIN_SCRIPT}"

if [ $? -ne 0 ]; then
    echo "Fout: PyInstaller is mislukt."
    exit 1
fi

echo "--- Stap 2: AppDir voorbereiden ---"
# Opschonen oude AppDir
rm -rf "${APPDIR_PATH}"
mkdir -p "${APPDIR_PATH}/usr/bin"

# Kopieer de PyInstaller output naar de AppDir
cp "${DIST_DIR}/${APP_NAME}" "${APPDIR_PATH}/usr/bin/"

# Maak noodzakelijke bestanden voor appimagetool (Desktop file en Icon)
cp assets/default_icon.svg "${APPDIR_PATH}/${APP_NAME}.svg"

cat > "${APPDIR_PATH}/${APP_NAME}.desktop" <<EOF
[Desktop Entry]
Name=${APP_NAME}
Exec=${APP_NAME}
Icon=${APP_NAME}
Type=Application
Categories=Game;
Terminal=false
EOF

# Maak de AppRun symlink
ln -s "usr/bin/${APP_NAME}" "${APPDIR_PATH}/AppRun"

echo "--- Stap 3: Genereren van AppImage met appimagetool ---"
export ARCH=$(uname -m)
"${APPIMAGETOOL_PATH}" deploy "${APPDIR_PATH}/${APP_NAME}.desktop" --overwrite

mv dist/GameDotExe dist/GameDotExe-${ARCH}.AppImage
echo "--- AppImage generatie voltooid! ---"
echo "Je AppImage zou moeten staan in de '${DIST_DIR}' map."