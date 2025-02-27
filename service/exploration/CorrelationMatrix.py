import os
import polars as pl
from PyQt6.QtWidgets import QMessageBox
import rpy2.robjects as ro
import rpy2.robjects.lib.grdevices as grdevices

def run_correlation_matrix(parent):
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
            print("corplot exists!")
            plot_path =[]
            plot_path.append("correlation_plot.png")
            grdevices.png(file=plot_path, width=800, height=600)
            ro.r('print(correlation_plot)')
            grdevices.dev_off()
            parent.plot = plot_path

    except Exception as e:
        # Menampilkan dialog error jika terjadi masalah
        error_dialog = QMessageBox()
        error_dialog.setIcon(QMessageBox.Icon.Critical)
        error_dialog.setText("Error")
        error_dialog.setInformativeText(str(e))
        error_dialog.exec()
        print("Error occurred: ", str(e))
