import os
import polars as pl
from PyQt6.QtWidgets import QMessageBox
import rpy2.robjects as ro
import rpy2.robjects.lib.grdevices as grdevices
from rpy2.robjects import pandas2ri

def run_correlation_matrix(parent):
    """
    Executes a correlation matrix analysis using R and returns the results.
    Parameters:
    parent (object): An object that contains the following attributes:
        - activate_R(): Method to activate R environment.
        - model1: An object with a method get_data() that returns a Polars DataFrame.
        - model2: An object with a method get_data() that returns a Polars DataFrame.
        - r_script: A string containing the R script to be executed.
        - result: A string to store the correlation matrix result.
        - plot: A list to store the path of the generated correlation plot.
        - error: A boolean to indicate if an error occurred.
    The function performs the following steps:
    1. Activates the R environment.
    2. Retrieves data from model1 and model2, concatenates them, and removes null values.
    3. Converts the Polars DataFrame to an R DataFrame.
    4. Loads necessary R libraries and prepares the data in R.
    5. Executes the provided R script to generate the correlation matrix.
    6. Captures the correlation matrix result and stores it in the parent.result attribute.
    7. Checks if a correlation plot is generated and saves it to a file if it exists.
    8. Handles any exceptions by setting the parent.error attribute and storing the error message in parent.result.
    """
    
    import rpy2_arrow.polars as rpy2polars

    # Aktivasi R
    parent.activate_R()
    pandas2ri.activate()

    # Mengambil data dari model1 dan model2
    df1 = parent.model1.get_data()
    df2 = parent.model2.get_data()
    df = pl.concat([df1, df2], how="horizontal")
    df = df.filter(~pl.all_horizontal(pl.all().is_null()))

    # Mengonversi DataFrame Polars ke R DataFrame
    with rpy2polars.converter.context() as cv_ctx:
        r_df = rpy2polars.converter.py2rpy(df)
        ro.globalenv['r_df'] = r_df

    try:
        # Memuat library R yang diperlukan
        ro.r('suppressMessages(library(tidyr))')
        ro.r('suppressMessages(library(ggcorrplot))')
        ro.r('rm(list=ls()[ls() != "r_df"])')

        # Menyiapkan data di R
        ro.r('data <- as.data.frame(r_df)')
        ro.r(parent.r_script)

        result_tables = {}
        result_plots = []

        # Daftar metode yang mungkin digunakan
        methods = ["pearson", "spearman", "kendall"]

        for method in methods:
            matrix_name = f"correlation_matrix_{method}"
            plot_name = f"correlation_plot_{method}"

            if ro.r(f'exists("{matrix_name}")')[0]:
                # Ambil tabel korelasi
                matrix_df = ro.r(f'as.data.frame({matrix_name})')
                pandas_df = pandas2ri.rpy2py(matrix_df)
                correlation_df = pl.from_pandas(pandas_df)
                result_tables[f"{method.title()} Correlation"] = correlation_df

            if ro.r(f'exists("{plot_name}")')[0]:
                # Simpan plot korelasi ke file
                plot_path = f"{plot_name}.png"
                grdevices.png(file=plot_path, width=800, height=600)
                ro.r(f'print({plot_name})')
                grdevices.dev_off()
                result_plots.append(plot_path)

        parent.result = result_tables
        parent.plot = result_plots if result_plots else None

    except Exception as e:
        parent.error = True
        parent.result = str(e)

