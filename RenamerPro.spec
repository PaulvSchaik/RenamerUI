# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

# Collect all CustomTkinter assets (themes, fonts, images)
ctk_datas, ctk_binaries, ctk_hidden = collect_all('customtkinter')

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=ctk_binaries,
    datas=ctk_datas,
    hiddenimports=ctk_hidden + [
        'PIL._tkinter_finder',
        'metadata',
        'utils',
        'google.genai',
        'google.genai.types',
        'fitz',
        'dotenv',
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=['watchdog'],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='RenamerPro',
    debug=False,
    strip=False,
    upx=False,
    console=False,          # geen terminal venster
    argv_emulation=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    name='RenamerPro',
)

app = BUNDLE(
    coll,
    name='RenamerPro.app',
    icon=None,
    bundle_identifier='nl.paul.renamerPro',
    info_plist={
        'CFBundleDisplayName': 'RenamerPro',
        'CFBundleName': 'RenamerPro',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0',
        'NSHighResolutionCapable': True,
        'NSRequiresAquaSystemAppearance': False,   # dark mode support
        'LSMinimumSystemVersion': '12.0',
    },
)
