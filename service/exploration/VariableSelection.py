import polars as pl
from PyQt6.QtWidgets import QMessageBox

import rpy2.robjects as ro
import rpy2_arrow.polars as rpy2polars

def run_variable_selection(parent):
    """
    Run data summary using Python (Polars) and R with additional debugging.
    """
    parent.activate_R()  # Activate R if needed

    # Get data from the model
    df1 = parent.model1.get_data()
    df2 = parent.model2.get_data()

    # Merge data using Polars
    df = pl.concat([df1, df2], how="horizontal")
    df = df.drop_nulls()  # Remove null data

    # Convert Polars DataFrame to R DataFrame
    try:
        with rpy2polars.converter.context() as cv_ctx:
            r_df = rpy2polars.converter.py2rpy(df)
            ro.globalenv['r_df'] = r_df
    except Exception as e:
        print("[ERROR] Failed to convert to R DataFrame:", str(e))
        return

    try:
        ro.r('suppressMessages(library(car))')
        ro.r('rm(list=ls()[ls() != "r_df"])')
        ro.r('data <- as.data.frame(r_df)')

        # Run R script
        ro.r(parent.r_script)

        # Check objects in the R environment
        existing_objects = ro.r('ls()')

        result_strings = []

        # List of methods used
        methods = ["forward", "backward", "both"]

        for method in methods:
            result_var = f"{method}_result"
            if result_var in existing_objects:
                result_output = ro.r(f'capture.output(print({result_var}))')
                result_strings.append(f"{method.capitalize()} Result:\n" + "\n".join(result_output) + "\n")

            # If trace is not active, only display result
            else:
                if result_var in existing_objects:
                    result_output = ro.r(f'capture.output(print({result_var}))')
                    result_strings.append(f"{method.capitalize()} Result:\n" + "\n".join(result_output) + "\n")

        # Save the result to parent.result
        parent.result = "\n\n".join(result_strings)

    except Exception as e:
        parent.error = True
        parent.result = str(e)
        return
