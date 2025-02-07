import os
import polars as pl
from PyQt6.QtWidgets import QMessageBox
import rpy2.robjects as ro
import rpy2.robjects.lib.grdevices as grdevices

def run_scatterplot(parent):
    import rpy2_arrow.polars as rpy2polars

    parent.activate_R()
    df1 = parent.model1.get_data()
    df2 = parent.model2.get_data()
    df = pl.concat([df1, df2], how="horizontal")
    df = df.drop_nulls()  # Remove null values

    # Convert Polars DataFrame to R DataFrame
    with rpy2polars.converter.context() as cv_ctx:
        r_df = rpy2polars.converter.py2rpy(df)
        ro.globalenv['r_df'] = r_df

    try:
        # Load required R libraries
        ro.r('suppressMessages(library(ggplot2))')

        # Remove previous scatterplot objects from the R environment
        ro.r('rm(list=ls(pattern="^scatterplot_"))')

        # Set up data in R
        ro.r('data <- as.data.frame(r_df)')

        # Execute the script created in the dialog
        script = parent.r_script
        ro.r(script)

        # Retrieve the list of scatterplot variables in the R environment
        r_objects = ro.r("ls()")  # List all objects in R
        scatterplot_vars = [obj for obj in r_objects if obj.startswith("scatterplot_")]

        plot_paths = []

        for plot_name in scatterplot_vars:
            plot_path = f"{plot_name}.png"
            grdevices.png(file=plot_path, width=800, height=600)
            ro.r(f"print({plot_name})")
            grdevices.dev_off()
            plot_paths.append(plot_path)

        print("Saved scatterplots:", plot_paths)

        # Store the results in parent (optional)
        parent.plot = plot_paths  # All plots are stored in a list

    except Exception as e:
        # Display an error dialog if an issue occurs
        error_dialog = QMessageBox()
        error_dialog.setIcon(QMessageBox.Icon.Critical)
        error_dialog.setText("Error")
        error_dialog.setInformativeText(str(e))
        error_dialog.exec()
