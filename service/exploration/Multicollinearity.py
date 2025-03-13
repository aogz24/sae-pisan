import polars as pl
from PyQt6.QtWidgets import QMessageBox
import rpy2.robjects as ro
import rpy2_arrow.polars as rpy2polars

def run_multicollinearity(parent):
    """
    Run multicollinearity analysis using R from within a Python environment.
    This function performs the following steps:
    1. Activates R environment.
    2. Retrieves data from two models in the parent object.
    3. Combines the data using Polars and removes any null values.
    4. Converts the Polars DataFrame to an R DataFrame.
    5. Loads the 'car' library in R and prepares the data for analysis.
    6. Executes a pre-generated R script stored in the parent object.
    7. Captures and stores the output of the regression model and VIF (Variance Inflation Factor) analysis.
    8. Combines the results and stores them in the parent object.
    Parameters:
    parent (object): An object that contains the models, R script, and attributes to store results and errors.
    Raises:
    ValueError: If no R script has been generated in the parent object.
    Exception: If any other error occurs during the execution, it is caught and stored in the parent object.
    """
    
    parent.activate_R()  # Pastikan R aktif

    # Ambil data dari model
    df1 = parent.model1.get_data()
    df2 = parent.model2.get_data()

    # Gabungkan data menggunakan Polars
    df = pl.concat([df1, df2], how="horizontal")
    df = df.drop_nulls()  # Hapus data kosong

    # Konversi Polars DataFrame ke R DataFrame
    with rpy2polars.converter.context() as cv_ctx:
        r_df = rpy2polars.converter.py2rpy(df)
        ro.globalenv['r_df'] = r_df  # Simpan ke lingkungan global R

    try:
        ro.r('suppressMessages(library(car))')
        # Bersihkan variabel di R, tetapi simpan `r_df`
        ro.r('rm(list=ls()[ls() != "r_df"])')
        ro.r('data <- as.data.frame(r_df)')

        # Pastikan script R telah dihasilkan
        if not hasattr(parent, 'r_script'):
            raise ValueError("No R script has been generated.")

        # Jalankan script R
        ro.r(parent.r_script)

        # Simpan hasil model regresi (lm) jika ada
        if parent.reg_model:
            regression_model_output = ro.r('capture.output(print(regression_model))')
            regression_result = "\n".join(regression_model_output)
        else:
            regression_result = ""

        # Ambil output hasil perhitungan VIF
        vif_output = ro.r('capture.output(print(vif_values))')
        vif_result = "\n".join(vif_output)  

        # Gabungkan hasil dalam satu variabel tanpa menghapus hasil lm sebelumnya
        final_result = f"{regression_result}\nVIF Value:\n{vif_result}"

        # Simpan hasil ke dalam parent.result
        parent.result = final_result

    except Exception as e:
        parent.error = True
        parent.result = str(e)
        return