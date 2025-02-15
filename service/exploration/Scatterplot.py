import os
import polars as pl
from PyQt6.QtWidgets import QMessageBox
import rpy2.robjects as ro
import rpy2.robjects.lib.grdevices as grdevices

def run_scatterplot(parent):
    import rpy2_arrow.polars as rpy2polars

    try:
        # Aktivasi R
        parent.activate_R()

        # Ambil data dari model1 dan model2
        df1 = parent.model1.get_data()
        df2 = parent.model2.get_data()

        # Gabungkan data menjadi satu dataframe
        df = pl.concat([df1, df2], how="horizontal")
        df = df.drop_nulls()  # Hapus nilai yang null

        # Convert Polars DataFrame ke R DataFrame
        with rpy2polars.converter.context() as cv_ctx:
            r_df = rpy2polars.converter.py2rpy(df)
            ro.globalenv['r_df'] = r_df

        # Muat library R yang diperlukan
        ro.r('suppressMessages(library(GGally))')
        ro.r('rm(list=ls()[ls() != "r_df"])')

        # Set data dalam R
        ro.r('data <- as.data.frame(r_df)')

        # Ambil script R yang dibuat dari dialog
        script = parent.r_script

        # Jalankan script R
        ro.r(script)

        # Ambil daftar objek di R
        r_objects = ro.r("ls()")  # Daftar semua objek di R

        # Cari objek scatterplot
        scatterplot_vars = [obj for obj in r_objects if obj.startswith("scatterplot_")]

        plot_paths = []

        # Simpan scatterplot sebagai gambar
        for plot_name in scatterplot_vars:
            plot_path = f"{plot_name}.png"
            
            # Tentukan file output untuk gambar
            grdevices.png(file=plot_path, width=800, height=600)

            # Cetak plot
            ro.r(f"print({plot_name})")
            
            # Tutup device gambar
            grdevices.dev_off()

            # Simpan path gambar ke daftar
            plot_paths.append(plot_path)

        # Simpan hasil plot dalam parent (optional)
        parent.plot = plot_paths  # Semua plot disimpan dalam daftar

    except Exception as e:
        # Menampilkan dialog error jika ada masalah
        error_dialog = QMessageBox()
        error_dialog.setIcon(QMessageBox.Icon.Critical)
        error_dialog.setText("Error")
        error_dialog.setInformativeText(str(e))
        error_dialog.exec()
        # Debug: print error yang terjadi
        print("Error occurred:", str(e))
