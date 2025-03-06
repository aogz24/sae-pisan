import os
import polars as pl
from PyQt6.QtWidgets import QMessageBox

import rpy2.robjects as ro
import rpy2.robjects.lib.grdevices as grdevices

def run_scatterplot(parent):
    import rpy2_arrow.polars as rpy2polars

    try:
        # Activate R
        parent.activate_R()

        # Get data from model1 and model2
        df1 = parent.model1.get_data()
        df2 = parent.model2.get_data()

        # Merge the data into one dataframe
        df = pl.concat([df1, df2], how="horizontal")
        df = df.drop_nulls() 

        # Convert Polars DataFrame to R DataFrame
        with rpy2polars.converter.context() as cv_ctx:
            r_df = rpy2polars.converter.py2rpy(df)
            ro.globalenv['r_df'] = r_df

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
            plot_path = f"{plot_name}.png"
            
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
