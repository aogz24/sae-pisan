import polars as pl
from PyQt6.QtWidgets import QMessageBox
from service.modelling.running_model.convert_df import convert_df
from rpy2.rinterface_lib.embedded import RRuntimeError

def run_model_projection(parent):
    """
    Runs the model projection using R scripts and returns the results.
    Parameters:
    parent (object): The parent object that contains the necessary methods and attributes for running the model projection.
    Returns:
    tuple: A tuple containing:
        - result (str): The result of the model projection or error message.
        - error (bool): A boolean indicating whether an error occurred.
        - df (polars.DataFrame or None): The projected data as a Polars DataFrame if successful, otherwise None.
    """
    
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