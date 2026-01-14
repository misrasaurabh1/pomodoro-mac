# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['pomodoro.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['rumps', 'Quartz', 'Quartz.CoreGraphics'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Pomodoro',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
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
    name='Pomodoro',
)
app = BUNDLE(
    coll,
    name='Pomodoro.app',
    icon='Pomodoro.icns',
    bundle_identifier='com.saurabhmisra.pomodoro',
)
