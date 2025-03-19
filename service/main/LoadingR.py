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
    r_script = """
            suppressPackageStartupMessages({
                r_home <- Sys.getenv("R_HOME")
                packages <- c("sae", "arrow", "sae.projection", "emdi", "xgboost", "LiblineaR", "kernlab", "GGally", "ggplot2", "ggcorrplot", "car", "nortest", "tidyr", "carData", "ggplot2", "ggcorrplot", "dplyr", "tseries")
                installed <- rownames(installed.packages(lib.loc=r_home))
                for (pkg in packages) {
                    if (!(pkg %in% installed)) {
                        install.packages(pkg, lib=r_home)
                    }
                }
                if (!("polars" %in% installed)) {
                    install.packages("polars", repos = "https://community.r-multiverse.org", lib=r_home)
                }
            })
            """
    ro.r(r_script)
    r_home = ro.r('Sys.getenv("R_HOME")')[0]
    os.environ['R_LIBS_USER'] = r_home
    # Initialize rpy2 with the new library location
    ro.r(f'.libPaths("{r_home}")')
    splash.update_message()