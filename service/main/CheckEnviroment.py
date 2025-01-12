import os
import subprocess

def check_environment(path):
    if not os.path.exists(path):
        url = "https://cran.r-project.org/bin/windows/base/R-4.4.2-win.exe"
        installer_path = os.path.join(os.path.expanduser("~"), "R-latest.exe")

        subprocess.check_call(['curl', '-o', installer_path, url])

        # Define the relative path for the R installation directory
        relative_path = os.path.join(os.path.dirname(__file__), 'R', 'R-4.4.2')

        # Run the installer silently with the correct directory
        # Run the installer silently with the correct directory
        subprocess.check_call([installer_path, '/SILENT', f'/DIR={relative_path}'])
    os.environ['R_HOME'] = path