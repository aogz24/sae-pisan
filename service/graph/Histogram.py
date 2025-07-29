import os
import polars as pl
from PyQt6.QtWidgets import QMessageBox
import rpy2.robjects as ro
import rpy2.robjects.lib.grdevices as grdevices
from service.utils.convert import get_data

def run_histogram(parent):
    """
    Executes an R script to generate histograms from data in a Polars DataFrame.
    This function performs the following steps:
    1. Activates the R environment using the parent object's `activate_R` method.
    2. Retrieves data from two models in the parent object and concatenates them into a single Polars DataFrame.
    3. Drops any null values from the DataFrame.
    4. Converts the Polars DataFrame to an R DataFrame and assigns it to the R global environment.
    5. Loads required R libraries (`ggplot2` and `tidyr`).
    6. Sets up the data in R and executes a script provided by the parent object.
    7. Identifies histogram variables created by the script in the R environment.
    8. Generates PNG files for each histogram and stores their paths in the parent object's `plot` attribute.
    9. Handles any exceptions by setting the parent object's `error` attribute to True and storing the error message in the `result` attribute.
    Args:
        parent (object): An object that contains methods and attributes required for the function, including:
            - `activate_R()`: Method to activate the R environment.
            - `model1.get_data()`: Method to retrieve data from the first model.
            - `model2.get_data()`: Method to retrieve data from the second model.
            - `r_script`: A string containing the R script to be executed.
            - `plot`: Attribute to store the paths of generated histogram PNG files.
            - `error`: Attribute to indicate if an error occurred.
            - `result`: Attribute to store the error message if an exception is raised.
    """
    
    import rpy2_arrow.polars as rpy2polars

    parent.activate_R()
    df1 = parent.model1.get_data()
    df2 = parent.model2.get_data()
    df = pl.concat([df1, df2], how="horizontal")
    df = df.filter(~pl.all_horizontal(pl.all().is_null()))
    get_data(parent,df)

    try:
        # Load required R libraries
        ro.r('suppressMessages(library(ggplot2))')
        ro.r('suppressMessages(library(tidyr))')
        ro.r('rm(list=ls()[ls() != "r_df"])')

        # Set up data in R
        ro.r('data <- as.data.frame(r_df)')

        # Execute the script created in the dialog
        script = parent.r_script
        ro.r(script)

        # Retrieve the list of histogram variables in the R environment
        r_objects = ro.r("ls()")  # List all objects in R
        histogram_vars = [obj for obj in r_objects if obj.startswith("histogram_")]

        plot_paths = []

        for plot_name in histogram_vars:
            appdata_dir = os.path.join(os.getenv("APPDATA"), "saePisan")
            os.makedirs(appdata_dir, exist_ok=True)
            plot_path = os.path.join(appdata_dir, f"{plot_name}.png")
            grdevices.png(file=plot_path, width=800, height=600)
            ro.r(f"print({plot_name})")
            grdevices.dev_off()
            plot_paths.append(plot_path)

        parent.plot = plot_paths  
        parent.result = {"Graph": "Histogram"}

    except Exception as e:
        parent.error = True
        parent.result = str(e)
        return
