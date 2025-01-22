import polars as pl
from PyQt6.QtWidgets import QMessageBox

def run_normality_test(parent):
    import rpy2.robjects as ro
    import rpy2_arrow.polars as rpy2polars
    parent.activate_R()
    df1 = parent.model1.get_data()
    df2 = parent.model2.get_data()
    df = pl.concat([df1, df2], how="horizontal")
    print(df)
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

        # Menjalankan script R dari parent
        ro.r(parent.r_script)

        # Mengambil hasil uji normalitas
        ro.r('results <- do.call(rbind, normality_results)')
        result_str = ro.r('capture.output(print(normality_results))')
        result = "\n".join(result_str)

        # Konversi hasil R ke Python
        results = ro.conversion.rpy2py(ro.globalenv['results'])
        parent.result = str(result)

    except Exception as e:
        # Menampilkan dialog error jika terjadi masalah
        error_dialog = QMessageBox()
        error_dialog.setIcon(QMessageBox.Icon.Critical)
        error_dialog.setText("Error")
        error_dialog.setInformativeText(str(e))
        error_dialog.exec()
