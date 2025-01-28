import os
import polars as pl
from PyQt6.QtWidgets import QMessageBox
import rpy2.robjects as ro
import rpy2.robjects.lib.grdevices as grdevices

def run_normality_test(parent):
    import rpy2.robjects as ro
    import rpy2_arrow.polars as rpy2polars
    parent.activate_R()
    df1 = parent.model1.get_data()
    df2 = parent.model2.get_data()
    df = pl.concat([df1, df2], how="horizontal")
    df = df.drop_nulls()  # Menghapus data null

    # Konversi Polars DataFrame ke R DataFrame
    with rpy2polars.converter.context() as cv_ctx:
        r_df = rpy2polars.converter.py2rpy(df)
        ro.globalenv['r_df'] = r_df

    try:
        # Memuat library R yang diperlukan
        ro.r('suppressMessages(library(nortest))')
        ro.r('suppressMessages(library(tseries))')

        # Mengatur data di R
        ro.r('data <- as.data.frame(r_df)')

        # Jalankan script yang dibuat di dialog
        script = parent.r_script
        ro.r(script)

        # Simpan hasil uji normalitas
        result = ro.r("capture.output(print(normality_results))")
        result_text = "\n".join(result)

        # Generate plot (jika ada histogram atau qqplot di script)
        plot_paths = []
        for plot_name in ["histogram", "qqplot"]:
            if ro.r(f"exists('{plot_name}')")[0]:
                plot_path = f"temp_{plot_name}.png"
                grdevices.png(file=plot_path, width=800, height=600)
                ro.r(f"print({plot_name})")
                grdevices.dev_off()
                plot_paths.append(plot_path)

        # Simpan hasil ke model
        parent.result = result_text
        parent.plot = plot_paths


    except Exception as e:
        # Menampilkan dialog error jika terjadi masalah
        error_dialog = QMessageBox()
        error_dialog.setIcon(QMessageBox.Icon.Critical)
        error_dialog.setText("Error")
        error_dialog.setInformativeText(str(e))
        error_dialog.exec()
