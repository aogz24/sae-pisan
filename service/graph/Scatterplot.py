import os
import polars as pl

import rpy2.robjects as ro
import rpy2.robjects.lib.grdevices as grdevices
from service.convert_df import convert_df

def run_scatterplot(parent):
    """
    Generates scatterplots using data from two models and saves them as images.
    This function activates the R environment, retrieves data from two models,
    merges the data, converts it to an R DataFrame, and executes an R script
    to generate scatterplots. The scatterplots are then saved as PNG images.
    Args:
        parent: An object that contains the following attributes:
            - activate_R(): A method to activate the R environment.
            - model1: An object with a get_data() method that returns a Polars DataFrame.
            - model2: An object with a get_data() method that returns a Polars DataFrame.
            - r_script: A string containing the R script to be executed.
            - plot: An attribute to store the list of generated plot image paths.
            - error: An attribute to indicate if an error occurred.
            - result: An attribute to store the error message if an error occurred.
    Raises:
        Exception: If any error occurs during the execution, it sets the parent's
                   error attribute to True and stores the error message in the
                   parent's result attribute.
    """
    
    # Activate R
    parent.activate_R()

    # Get data from model1 and model2
    df1 = parent.model1.get_data()
    df2 = parent.model2.get_data()

    # Merge the data into one dataframe
    df = pl.concat([df1, df2], how="horizontal")
    df = df.filter(~pl.all_horizontal(pl.all().is_null()))
    convert_df(df, parent)

    try:

        # Load required R libraries
        ro.r('suppressMessages(library(GGally))')
        ro.r('rm(list=ls()[ls() != "r_df"])')

        # Set data in R
        ro.r('data <- as.data.frame(r_df)')

        # Get the R script created from the dialog
        script = parent.r_script

        # Run the R script
        ro.r(script)

        # Get the list of objects in R
        r_objects = ro.r("ls()")  

        # Find scatterplot objects
        scatterplot_vars = [obj for obj in r_objects if obj.startswith("scatterplot_")]

        plot_paths = []

        # Save scatterplots as images
        for plot_name in scatterplot_vars:
            appdata_dir = os.path.join(os.getenv("APPDATA"), "saePisan")
            os.makedirs(appdata_dir, exist_ok=True)
            plot_path = os.path.join(appdata_dir, f"{plot_name}.png")
            
            # Specify the output file for the image
            grdevices.png(file=plot_path, width=800, height=600)

            # Print the plot
            ro.r(f"print({plot_name})")
            
            # Close the image device
            grdevices.dev_off()

            # Save the image path to the list
            plot_paths.append(plot_path)

        # Save the plot results in the parent (optional)
        parent.plot = plot_paths  # All plots are stored in a list

    except Exception as e:
        parent.error = True
        parent.result = str(e)
        print(str(e))
        return
