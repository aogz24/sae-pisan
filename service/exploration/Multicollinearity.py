import polars as pl
import rpy2.robjects as ro
from rpy2.robjects import pandas2ri
from service.utils.convert import get_data

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
    pandas2ri.activate()
    parent.activate_R()  # Pastikan R aktif
    # Ambil data dari model
    df1 = parent.model1.get_data()
    df2 = parent.model2.get_data()

    # Gabungkan data menggunakan Polars
    df = pl.concat([df1, df2], how="horizontal")
    df = df.filter(~pl.all_horizontal(pl.all().is_null()))
    df = df.filter(~pl.all_horizontal(pl.all().is_null()))
    get_data(parent,df)

    try:
        ro.r('suppressMessages(library(car))')
        ro.r('suppressMessages(library(tibble))')  # untuk rownames_to_column

        # Bersihkan environment di R kecuali r_df
        ro.r('rm(list=ls()[ls() != "r_df"])')
        ro.r('data <- as.data.frame(r_df)')

        # Jalankan script R dari parent
        ro.r(parent.r_script)

        result = {}
        result["Pre-Modeling"] = "Multicollinearity Analysis"

        if parent.reg_model:
            # Ambil formula regresi sebagai teks string
            regression_formula_r = ro.r('deparse(regression_model$call)')
            regression_formula = " ".join(regression_formula_r)
            result["Regression Formula"] = regression_formula

            # Ambil intercept (koefisien), ubah rownames jadi kolom
            ro.r('intercept_df <- tibble::rownames_to_column(as.data.frame(regression_model$coefficients), var = "Variable")')
            intercept_df = ro.r('intercept_df')
            intercept_polars = pl.from_pandas(pandas2ri.rpy2py(intercept_df))
            intercept_polars = intercept_polars.with_columns(
                pl.col("Variable").str.replace_all("`", "")
            )
            intercept_polars = intercept_polars.rename({"regression_model$coefficients": "Coefficient"})
            result["Intercept"] = intercept_polars

        # Ambil VIF dan ubah rownames jadi kolom
        ro.r('vif_df <- tibble::rownames_to_column(as.data.frame(vif_values), var = "Variable")')
        vif_df = ro.r('vif_df')
        vif_polars_df = pl.from_pandas(pandas2ri.rpy2py(vif_df))
        vif_polars_df = vif_polars_df.with_columns(
            pl.col("Variable").str.replace_all("`", "")
        )
        vif_polars_df = vif_polars_df.rename({"vif_values": "VIF"})
        result["VIF Table"] = vif_polars_df

        # Simpan hasil ke parent
        parent.result = result

    except Exception as e:
        parent.error = True
        parent.result = str(e)
        return