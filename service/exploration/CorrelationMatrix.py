import os
import polars as pl
from PyQt6.QtWidgets import QMessageBox
import rpy2.robjects as ro
import rpy2.robjects.lib.grdevices as grdevices

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

    # Mengambil data dari model1 dan model2
    df1 = parent.model1.get_data()
    df2 = parent.model2.get_data()
    df = pl.concat([df1, df2], how="horizontal")
    df = df.drop_nulls()  # Menghapus nilai null

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

        # Mengeksekusi script yang dibuat pada dialog
        script = parent.r_script  # Script R yang dihasilkan di dialog
        ro.r(script)

        correlation_result = ro.r('capture.output(print(correlation_matrix))')
        correlation_text = "\n".join(correlation_result)  # Gabungkan menjadi teks
        parent.result = correlation_text  # Simpan sebagai string

        # Mengecek apakah ada plot korelasi yang dihasilkan
        correlation_plot_exists = ro.r('exists("correlation_plot")')

        if correlation_plot_exists[0]:
            plot_path =[]
            plot_path.append("correlation_plot.png")
            grdevices.png(file=plot_path, width=800, height=600)
            ro.r('print(correlation_plot)')
            grdevices.dev_off()
            parent.plot = plot_path

    except Exception as e:
        parent.error = True
        parent.result = str(e)
        return
