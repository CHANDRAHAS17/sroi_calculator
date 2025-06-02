# -*- mode: python ; coding: utf-8 -*-

# ✅ Define datas separately
datas = [
    ('NIRMAAN_logo.png', '.'),
    ('app.py', '.'),
]

a = Analysis(
    ['app_launcher.py'],
    pathex=['/Users/chandrahasjandhyala/Desktop/SROI GUI'],  
    binaries=[],
    datas=datas,  
    hiddenimports=[],
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
    a.binaries,
    a.datas,
    [],
    name='app_launcher',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

app = BUNDLE(
    exe,
    name='app_launcher.app',
    icon=None,
    bundle_identifier=None,
)
