import polars as pl
from PyQt6.QtWidgets import QMessageBox
from service.modelling.running_model.convert_df import convert_df
from rpy2.rinterface_lib.embedded import RRuntimeError

def run_model_eblup_unit(parent):
    """
    Runs the EBLUP (Empirical Best Linear Unbiased Prediction) model using R through rpy2.
    Parameters:
    parent (object): An object that contains the necessary methods and attributes to run the model.
                     It should have the following methods and attributes:
                     - activate_R(): Method to activate the R environment.
                     - model1.get_data(): Method to get the data for the model.
                     - r_script: An R script to be executed.
    Returns:
    tuple: A tuple containing:
           - result (str): The result of the model execution or error message.
           - error (bool): A flag indicating whether an error occurred.
           - df (polars.DataFrame or None): A DataFrame containing the model results with columns 'Domain', 'Eblup', 'Sample size', and 'MSE'.
                                            None if an error occurred.
    """
    
    import rpy2.robjects as ro
    parent.activate_R()
    df = parent.model1.get_data()
    df = df.drop_nulls()
    convert_df(df, parent)
    result = ""
    error = False
    try:
        ro.r('suppressMessages(library(sae))')
        ro.r('data <- as.data.frame(r_df)')
        try:
            ro.r(parent.r_script)  # Menjalankan skrip R
        except RRuntimeError as e:
            result = str(e)
            error = True
            return result, error, None
        ro.r('domain <- model$est$eblup$domain\n estimated_value <- model$est$eblup$eblup\n n_size <- model$est$eblup$sampsize \n mse <- model$mse$mse')
        result_str = ro.r('capture.output(print(model))')
        result = "\n".join(result_str)
        domain = ro.r('domain')
        estimated_value = ro.r('estimated_value')
        n_size = ro.r('n_size')
        mse = ro.r('mse')
        df = pl.DataFrame({
            'Domain': domain,
            'Eblup': estimated_value,
            'Sample size': n_size,
            'MSE': mse})
        error = False
        return result, error, df
        
    except Exception as e:
        error = True
        return str(e), error, None