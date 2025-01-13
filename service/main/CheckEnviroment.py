import os
import subprocess
import time
import errno

def check_environment(path):
    if not os.path.exists(path):
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
    # os.environ['R_HOME'] = path

    # Make R_HOME permanent by adding it to the user's environment variables
    if os.name == 'nt':
        subprocess.check_call(['setx', 'R_HOME', path])
    elif os.name == 'posix':
        bashrc_path = os.path.join(os.path.expanduser("~"), '.bashrc')
        with open(bashrc_path, 'r') as bashrc:
            lines = bashrc.readlines()
        with open(bashrc_path, 'w') as bashrc:
            for line in lines:
                if line.strip().startswith('export R_HOME='):
                    continue
                bashrc.write(line)
            bashrc.write(f'\nexport R_HOME={path}\n')