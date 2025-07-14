import rpy2.robjects as ro
from rpy2.robjects import pandas2ri
import os

def loadR(splash):
    """Loads and installs necessary R packages for the application.
    This function updates the splash screen message, activates the pandas2ri interface,
    and runs an R script to install required R packages if they are not already installed.
    The R packages include 'sae', 'arrow', 'sae.projection', 'emdi', 'xgboost', 'LiblineaR',
    'kernlab', 'GGally', 'ggplot2', 'ggcorrplot', 'car', and 'polars'.
    Args:
        splash: An object that handles the splash screen updates.
    Returns:
        None"""
    
    splash.update_message()
    pandas2ri.activate()
    from rpy2.robjects.packages import importr, isinstalled
    utils = importr('utils')
    r_home = str(ro.r('Sys.getenv("R_HOME")')[0])
    os.environ['R_LIBS_USER'] = r_home
    # Initialize rpy2 with the new library location
    ro.r(f'.libPaths("{r_home}")')
    lib_path = str(ro.r('.libPaths()[1]')[0])
    os.environ['R_LIBS_USER'] = lib_path
    ro.r(f'.libPaths("{lib_path}")')
    packages = [
        "sae", "arrow", "sae.projection", "emdi", "xgboost", "LiblineaR",
        "kernlab", "GGally", "ggplot2", "ggcorrplot", "car", "nortest",
        "tidyr", "carData", "dplyr", "tseries", "FSelector", "glmnet"
    ]
    # Install CRAN packages if not installed
    for pkg in packages:
        if not isinstalled(pkg):
            utils.install_packages(pkg, lib=lib_path)
    # Install 'polars' from R-multiverse if not installed
    if not isinstalled("polars"):
        utils.install_packages("polars", repos="https://community.r-multiverse.org", lib=lib_path)
    splash.update_message()
    importr('sae', lib_loc=lib_path)
    importr('saeHB', lib_loc=lib_path)
    importr('emdi', lib_loc=lib_path)
    importr('sae.projection', lib_loc=lib_path)
    splash.update_message()