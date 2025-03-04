import polars as pl
from PyQt6.QtWidgets import QMessageBox
import rpy2.robjects as ro
import rpy2_arrow.polars as rpy2polars

def run_summary_data(parent):
    """
    Menjalankan ringkasan data menggunakan Python (Polars) dan R.
    """
    parent.activate_R()  # Aktifkan R jika diperlukan

    # Ambil data dari model
    df1 = parent.model1.get_data()
    df2 = parent.model2.get_data()

    # Gabungkan data menggunakan Polars
    df = pl.concat([df1, df2], how="horizontal")
    df = df.drop_nulls()  # Menghapus data null

    # Konversi Polars DataFrame ke R DataFrame
    with rpy2polars.converter.context() as cv_ctx:
        r_df = rpy2polars.converter.py2rpy(df)
        ro.globalenv['r_df'] = r_df

    try:
        # Mengatur data di R
        ro.r('data <- as.data.frame(r_df)')
        # Menjalankan script R dari parent
        ro.r(parent.r_script)

        # Mengambil hasil summary
        summary_str = ro.r('capture.output(print(summary_results))')
        summary_output = "\n".join(summary_str)

        # Simpan hasil summary ke dalam parent.result
        parent.result = str(summary_output)

    except Exception as e:
        # Menampilkan dialog error jika terjadi masalah
        error_dialog = QMessageBox()
        error_dialog.setIcon(QMessageBox.Icon.Critical)
        error_dialog.setText("Error")
        error_dialog.setInformativeText(str(e))
        error_dialog.exec()
        parent.error = str(e)
