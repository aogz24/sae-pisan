import os
import polars as pl
from PyQt6.QtWidgets import QMessageBox
import rpy2.robjects as ro
import rpy2.robjects.lib.grdevices as grdevices
from service.convert_df import convert_df

def run_lineplot(parent):
    """
    Executes an R script to generate line plots from data in a Polars DataFrame.
    This function performs the following steps:
    1. Activates the R environment in the parent object.
    2. Retrieves data from two models in the parent object and concatenates them horizontally.
    3. Removes null values from the concatenated DataFrame.
    4. Converts the Polars DataFrame to an R DataFrame.
    5. Loads required R libraries (ggplot2 and tidyr).
    6. Sets up the data in the R environment.
    7. Executes an R script provided by the parent object.
    8. Retrieves the list of line plot variables created in the R environment.
    9. Saves each line plot as a PNG file and stores the file paths in the parent object.
    Args:
        parent: An object that contains the following attributes and methods:
            - activate_R(): Method to activate the R environment.
            - model1: An object with a get_data() method that returns a Polars DataFrame.
            - model2: An object with a get_data() method that returns a Polars DataFrame.
            - r_script: A string containing the R script to be executed.
            - plot: An attribute to store the list of plot file paths (optional).
            - error: An attribute to indicate if an error occurred.
            - result: An attribute to store the error message if an error occurred.
    Raises:
        Exception: If any error occurs during the execution of the R script or plot generation.
    """
    
    import rpy2_arrow.polars as rpy2polars

    parent.activate_R()
    df1 = parent.model1.get_data()
    df2 = parent.model2.get_data()
    df = pl.concat([df1, df2], how="horizontal")
    df = df.filter(~pl.all_horizontal(pl.all().is_null()))
    convert_df(df, parent)

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

        # Retrieve the list of lineplot variables in the R environment
        r_objects = ro.r("ls()")  # List all objects in R
        lineplot_vars = [obj for obj in r_objects if obj.startswith("lineplot_")]

        plot_paths = []

        for plot_name in lineplot_vars:
            plot_path = f"{plot_name}.png"
            grdevices.png(file=plot_path, width=800, height=600)
            ro.r(f"print({plot_name})")
            grdevices.dev_off()
            plot_paths.append(plot_path)

        print("Saved lineplots:", plot_paths)

        # Store the results in parent (optional)
        parent.plot = plot_paths  # All plots are stored in a list

    except Exception as e:
        parent.error = True
        parent.result = str(e)
        return