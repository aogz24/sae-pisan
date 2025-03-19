import polars as pl
from PyQt6.QtWidgets import QMessageBox
from rpy2.rinterface_lib.embedded import RRuntimeError
from service.modelling.running_model.convert_df import convert_df

def run_model_eblup_pseudo(parent):
    """
    Runs the EBLUP (Empirical Best Linear Unbiased Prediction) pseudo model using R scripts.
    Parameters:
    parent (object): The parent object that contains necessary methods and attributes for running the model.
    Returns:
    tuple: A tuple containing:
        - result (str): The result of the R script execution or error message.
        - error (bool): A boolean indicating if an error occurred.
        - df (polars.DataFrame or None): A DataFrame containing the domain, EBLUP estimates, MSE, and RSE (%) if successful, otherwise None.
    The function performs the following steps:
    1. Activates the R environment.
    2. Retrieves and preprocesses the data.
    3. Executes the R script provided by the parent object.
    4. Extracts the estimated values, MSE, and domain from the R environment.
    5. Calculates the Relative Standard Error (RSE).
    6. Constructs a DataFrame with the results.
    7. Returns the results, error status, and DataFrame.
    """
    
    import rpy2.robjects as ro
    parent.activate_R()
    df = parent.model1.get_data()
    df = df.drop_nulls()
    convert_df(df, parent)
    result = ""
    error = False
    try:
        ro.r('suppressMessages(library("emdi", lib.loc=r_home))')
        ro.r('data <- as.data.frame(r_df)')
        try:
            ro.r(parent.r_script)  # Menjalankan skrip R
        except RRuntimeError as e:
            result = str(e)
            error = True
            return result, error, None
        ro.r('estimated_value <- getResponse(model)\n mse <- model$MSE$FH \n domain<-model$MSE$Domain')
        domain = ro.conversion.rpy2py(ro.globalenv['domain'])
        result_str = ro.r('capture.output(print(model))')
        result = "\n".join(result_str)
        estimated_value = ro.conversion.rpy2py(ro.globalenv['estimated_value'])
        mse = ro.conversion.rpy2py(ro.globalenv['mse'])
        vardir_var = ro.conversion.rpy2py(ro.globalenv['vardir_var'])
        estimated_value = estimated_value.flatten()
        vardir_var = vardir_var.to_numpy()[:, 0]
        rse = mse**0.5/estimated_value*100
        df = pl.DataFrame({
            'Domain': domain,
            'Eblup': estimated_value,
            'MSE': mse,
            'RSE (%)': rse})
        error = False
        return result, error, df
        
    except Exception as e:
        error = True
        return str(e), error, None