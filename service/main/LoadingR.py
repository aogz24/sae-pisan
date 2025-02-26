import rpy2.robjects as ro
from rpy2.robjects import pandas2ri

def loadR(splash):
    splash.update_message()
    pandas2ri.activate()
    r_script = """
            suppressPackageStartupMessages({
                r_home <- Sys.getenv("R_HOME")
                packages <- c("sae", "arrow", "sae.projection", "emdi", "xgboost", "LiblineaR", "kernlab", "GGally", "ggplot2", "ggcorrplot", "car")
                installed <- rownames(installed.packages())
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
    splash.update_message()