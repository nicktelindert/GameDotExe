# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('ui', 'ui'), ('assets', 'assets'), ('core/known_dos_games.json', 'core')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['PySide6.QtWebEngineCore', 'PySide6.QtWebEngineWidgets', 'PySide6.QtDesigner', 'PySide6.Qt3DCore', 'PySide6.QtCharts', 'PySide6.QtSql', 'PySide6.QtTest', 'PySide6.QtMultimedia', 'PySide6.QtBluetooth', 'PySide6.QtPositioning', 'tkinter', 'unittest'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='GameDotExe',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch='universal2',
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='GameDotExe',
)
app = BUNDLE(
    coll,
    name='GameDotExe.app',
    icon=None,
    bundle_identifier=None,
)
