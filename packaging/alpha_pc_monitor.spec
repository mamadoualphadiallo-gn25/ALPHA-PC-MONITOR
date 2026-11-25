# PyInstaller spec for ALPHA PC MONITOR (single-file Windows executable)
import os
from PyInstaller.utils.hooks import collect_submodules

PROJECT_ROOT = os.path.abspath(os.path.join(SPECPATH, os.pardir))
ENTRY_POINT = os.path.join(PROJECT_ROOT, "app", "main.py")

# pyqtgraph's optional OpenGL module is not used by this application.
hiddenimports = collect_submodules("pyqtgraph", filter=lambda name: not name.startswith("pyqtgraph.opengl"))

a = Analysis(
    [ENTRY_POINT],
    pathex=[PROJECT_ROOT],
    binaries=[],
    datas=[],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["OpenGL"],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="ALPHA-PC-MONITOR",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
)
