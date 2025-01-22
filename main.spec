import os
import subprocess
import time
import errno

# Define __file__ if not already defined
if '__file__' not in globals():
    import sys
    __file__ = sys.argv[0]

block_cipher = None

def check_environment(path):
    if not os.path.exists(path):
        if os.name == 'nt':
            url = "https://cran.r-project.org/bin/windows/base/R-4.4.2-win.exe"
            installer_path = os.path.join(os.path.expanduser("~"), "R-latest.exe")

            subprocess.check_call(['curl', '-o', installer_path, url])

            # Define the relative path for the R installation directory
            relative_path = os.path.join(os.path.dirname(__file__), 'R', 'R-4.4.2')

            # Run the installer silently with the correct directory
            for _ in range(20):  # Retry up to 20 times
                try:
                    subprocess.check_call([installer_path, '/SILENT', f'/DIR={relative_path}'])
                    break
                except subprocess.CalledProcessError as e:
                    if e.errno == errno.EACCES:  # Access error
                        time.sleep(1)  # Wait for 1 second before retrying
                    else:
                        raise
        elif os.name == 'posix':
            url = "https://cran.r-project.org/src/base/R-4/R-4.4.2.tar.gz"
            installer_path = os.path.join(os.path.expanduser("~"), "R-latest.tar.gz")
            extract_path = os.path.join(os.path.expanduser("~"), "R-4.4.2")

            subprocess.check_call(['curl', '-o', installer_path, url])
            subprocess.check_call(['tar', '-xzf', installer_path, '-C', os.path.expanduser("~")])

            # Configure and install R
            os.chdir(extract_path)
            subprocess.check_call(['./configure', '--prefix=' + path])
            subprocess.check_call(['make'])
            subprocess.check_call(['make', 'install'])
    
    # Set R_HOME environment variable
    os.environ['R_HOME'] = path

# Define the dynamic path to R and check the environment
r_home = os.path.join(os.path.dirname(__file__), 'R', 'R-4.4.2')
check_environment(r_home)

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('assets', 'assets'), ('R', 'R')],
    hiddenimports=['rpy2.robjects'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['PySide6', 'torch', 'cuda'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='main',
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
    upx=True,
    upx_exclude=[],
    name='main',
)