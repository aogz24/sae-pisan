import os
import subprocess
import time
import errno

# Define __file__ if not already defined
if '__file__' not in globals():
    import sys
    __file__ = sys.argv[0]

block_cipher = None

# Define the dynamic path to R and check the environment
r_home = os.path.join(os.path.dirname(__file__), 'R', 'R-4.4.2')
os.environ['R_HOME'] = r_home

a = Analysis(
    ['saePisan.py'],
    pathex=[],
    binaries=[],
    datas=[('assets', 'assets'), ('R', 'R'), ('file-data', 'file-data'), ('temp', 'temp')],
    hiddenimports=[
        'rpy2.robjects', "openpyxl", "fastexcel",
        'numpy', 'numpy.core._methods', 'numpy.lib.format'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['PySide6', 'torch', 'cuda', 'cv', 'cv2'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='saePisan',
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
    icon=['assets\\icon.ico'],
    env={"R_HOME": r_home}  # Ensure r_home is correctly set
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='saePisan'
)