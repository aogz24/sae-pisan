import polars as pl
from PyQt6.QtWidgets import QMessageBox
from service.modelling.running_model.convert_df import convert_df
from rpy2.rinterface_lib.embedded import RRuntimeError

def run_model_projection(parent):
    import rpy2.robjects as ro
    parent.activate_R()
    df = parent.model1.get_data()
    # df = df.drop_nulls()
    convert_df(df, parent)
    result = ""
    error = False
    try:
        ro.r('suppressMessages(library(sae.projection))')
        ro.r('data <- as.data.frame(r_df)')
        try:
            ro.r(parent.r_script)  # Menjalankan skrip R
        except RRuntimeError as e:
            result = str(e)
            error = True
            return result, error, None
        result_str = ro.r('capture.output(print(model))')
        result = "\n".join(result_str)
        ro.r('projection <- model$projection')
        proj = ro.conversion.rpy2py(ro.globalenv['projection'])
        df = pl.from_pandas(proj)
        error = False
        return result, error, df
        
    except Exception as e:
        error = True
        return str(e), error, None