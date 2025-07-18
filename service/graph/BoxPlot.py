import os
import polars as pl
from PyQt6.QtWidgets import QMessageBox
import rpy2.robjects as ro
import rpy2.robjects.lib.grdevices as grdevices
from service.utils.convert import get_data
import re

def run_box_plot(parent):
    """
    Executes a box plot generation process using R and Polars DataFrame.
    This function performs the following steps:
    1. Activates the R environment through the parent object.
    2. Retrieves data from two models in the parent object and concatenates them horizontally.
    3. Removes null values from the concatenated DataFrame.
    4. Converts the Polars DataFrame to an R DataFrame.
    5. Loads required R libraries (ggplot2 and tidyr).
    6. Sets up the data in the R environment.
    7. Executes an R script provided by the parent object.
    8. Retrieves the list of boxplot variables generated in the R environment.
    9. Saves each boxplot as a PNG file and stores the file paths in a list.
    10. Optionally stores the list of plot paths in the parent object.
    Args:
        parent: An object that provides the R environment activation method, data retrieval methods,
                and the R script to be executed. It also stores the resulting plot paths and error information.
    Raises:
        Exception: If any error occurs during the execution, it sets the error flag and result message in the parent object.
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

        # Extract list of boxplot variable names in order of appearance in the script
        boxplot_vars = re.findall(r'boxplot_\w+', script)
        print("Boxplot variables (ordered):", boxplot_vars)

        plot_paths = []

        for plot_name in boxplot_vars:
            # Ensure the directory exists
            appdata_dir = os.path.join(os.getenv("APPDATA"), "saePisan")
            os.makedirs(appdata_dir, exist_ok=True)
            plot_path = os.path.join(appdata_dir, f"{plot_name}.png")
            grdevices.png(file=plot_path, width=800, height=600)
            ro.r(f"print({plot_name})")
            grdevices.dev_off()
            plot_paths.append(plot_path)

        print("Saved boxplots:", plot_paths)

        # Store the results in parent (optional)
        parent.plot = plot_paths  # All plots are stored in a list

    except Exception as e:
        parent.error = True
        parent.result = str(e)
        return
