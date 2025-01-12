import rpy2.robjects as ro
from rpy2.robjects import pandas2ri

def loadR(splash):
    pandas2ri.activate()
    
    r_script = """
            suppressPackageStartupMessages({
                if (!require("sae", quietly = TRUE)) install.packages("sae"); library(sae);
                if (!require("polars", quietly = TRUE)) install.packages("polars", repos = "https://community.r-multiverse.org");
                if (!require("arrow", quietly = TRUE)) install.packages("arrow");
                if (!require("sae.projection", quietly = TRUE)) install.packages("sae.projection"); library(sae.projection);
            })
            """
    ro.r(r_script)
    