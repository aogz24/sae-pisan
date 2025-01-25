import os
import subprocess
import time
import errno

def check_environment(path):
    r_path = os.path.join(path, "bin")
    try:
        os.chdir(r_path)
        output = subprocess.check_output(['r', '--version'], stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        raise RuntimeError("R is not installed or not found in PATH.")
    
    if b"R version" in output:
        version_line = output.decode().split('\n')[0]
        version = version_line.split()[2]
    
    if (b"R version" not in output) or (version != "4.4.2"):
        if os.name == 'nt':
            url = "https://cran.r-project.org/bin/windows/base/R-4.4.2-win.exe"
            installer_path = os.path.join(os.path.expanduser("~"), "R-latest.exe")

            subprocess.check_call(['curl', '-o', installer_path, url])

            # Define the relative path for the R installation directory
            relative_path = os.path.join(os.path.dirname(__file__), 'R', 'R-4.4.2')

            # Run the installer silently with the correct directory
            for _ in range(20):  # Retry up to 5 times
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
    os.environ['R_HOME'] = path