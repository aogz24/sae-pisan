import polars as pl
from PyQt6.QtWidgets import QMessageBox

import rpy2.robjects as ro
import rpy2_arrow.polars as rpy2polars

def run_summary_data(parent):
    """
    Run data summary using Python (Polars) and R.
    """
    parent.activate_R()  

    # Get data from model
    df1 = parent.model1.get_data()
    df2 = parent.model2.get_data()

    # Combine data using Polars
    df = pl.concat([df1, df2], how="horizontal")
    df = df.drop_nulls()  # Remove null data

    # Convert Polars DataFrame to R DataFrame
    with rpy2polars.converter.context() as cv_ctx:
        r_df = rpy2polars.converter.py2rpy(df)
        ro.globalenv['r_df'] = r_df

    try:
        # Set data in R
        ro.r('data <- as.data.frame(r_df)')
        # Run R script from parent
        ro.r(parent.r_script)

        # Get summary results
        summary_str = ro.r('capture.output(print(summary_results))')
        summary_output = "\n".join(summary_str)

        # Save summary results to parent.result
        parent.result = str(summary_output)

    except Exception as e:
        parent.result = str(e)
        parent.error = True
