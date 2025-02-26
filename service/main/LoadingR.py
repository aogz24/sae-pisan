import rpy2.robjects as ro
from rpy2.robjects import pandas2ri

def loadR(splash):
    splash.update_message()
    pandas2ri.activate()
    r_script = """
            suppressPackageStartupMessages({
                r_home <- Sys.getenv("R_HOME")
                if (!require("sae", quietly = TRUE)) install.packages("sae", lib=r_home); library(sae, lib.loc=r_home);
                if (!require("polars", quietly = TRUE)) install.packages("sae", lib=r_home); library(sae, lib.loc=r_home);
                if (!require("arrow", quietly = TRUE)) install.packages("arrow", lib=r_home);
                if (!require("sae.projection", quietly = TRUE)) install.packages("sae.projection", lib=r_home); library(sae.projection, lib.loc=r_home);
                if (!require("emdi", quietly = TRUE)) install.packages("emdi", lib=r_home); library(emdi, lib.loc=r_home);
                if (!require("xgboost", quietly = TRUE)) install.packages("xgboost", lib=r_home);
                if (!require("LiblineaR", quietly = TRUE)) install.packages("LiblineaR", lib=r_home);
                if (!require("kernlab", quietly = TRUE)) install.packages("kernlab", lib=r_home);
            })
            """
    ro.r(r_script)
    splash.update_message()
    