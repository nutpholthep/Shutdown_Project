# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

datas = []
binaries = []
hiddenimports = ['pystray', 'pystray._win32', 'PIL', 'PIL._imagingtk', 'PIL._tkinter_finder']

ctk_datas, ctk_binaries, ctk_hiddenimports = collect_all('customtkinter')
datas += ctk_datas
binaries += ctk_binaries
hiddenimports += ctk_hiddenimports

a = Analysis(
    ['shutdown_scheduler.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
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
    name='ShutdownScheduler',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='app_icon.ico',
    version='file_version_info.txt',
    uac_admin=False,
)

