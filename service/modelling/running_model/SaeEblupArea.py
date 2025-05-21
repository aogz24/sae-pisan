import polars as pl
from PyQt6.QtWidgets import QMessageBox
from rpy2.rinterface_lib.embedded import RRuntimeError
from service.modelling.running_model.convert_df import convert_df

def run_model_eblup_area(parent):
    """
    Runs the EBLUP (Empirical Best Linear Unbiased Prediction) area model using the provided parent object.
    Parameters:
    parent (object): The parent object that contains necessary methods and attributes for running the model.
                     It should have the following methods and attributes:
                     - activate_R(): Method to activate R environment.
                     - model1.get_data(): Method to get the data for the model.
                     - r_script: An R script to be executed.
    Returns:
    tuple: A tuple containing:
           - result (str): The result of the model execution or error message.
           - error (bool): A flag indicating whether an error occurred.
           - df (polars.DataFrame or None): A DataFrame containing the estimated values, MSE, and RSE if the model runs successfully, otherwise None.
    """
    
    import rpy2.robjects as ro
    parent.activate_R()
    df = parent.model1.get_data()
    df = df.drop_nulls()
    result = ""
    error = False
    convert_df(df, parent)
    try:
        ro.r('suppressMessages(library(sae))')
        ro.r('data <- as.data.frame(r_df)')
        try:
            ro.r(parent.r_script)  # Menjalankan skrip R
        except RRuntimeError as e:
            result = str(e)
            error = True
            return result, error, None
        ro.r('estimated_value <- model$est$eblup\n mse <- model$mse \n method <- model$est$fit$method \n convergence<-model$est$fit$convergence \n iterations <- model$est$fit$iterations \n refvar <- model$est$fit$refvar \n goodness <-model$est$fit$goodness')
        method = ro.globalenv['method']
        convergence = ro.globalenv['convergence']
        if isinstance(convergence, ro.vectors.BoolVector):
            convergence = "Yes" if bool(convergence[0]) else "NO"
        else:
            convergence = "Not Converged"
        itteration = ro.globalenv['iterations']
        itteration = int(float(itteration[0]))
        refvar = ro.globalenv['refvar']
        refvar = int(float(refvar[0]))
        goodness_r = ro.conversion.rpy2py(ro.globalenv['goodness'])
        goodness = pl.DataFrame({
            'Logarithmic Likelihood': [goodness_r[0]],
            'Akaike Information Criterion ( AIC )': [goodness_r[1]],
            'Bayesian Information Criterion (BIC)': [goodness_r[2]],
            'Kullback Information Criterion (KIC)': [goodness_r[3]],
        })
        
        results = {
            "Model": "EBLUP Area Level",
            "Method": method,
            "Convergence": convergence,
            "Number of Iterations Performed by The Fisher-scoring Algorithm": itteration,
            "Random Effect Variance": refvar,
            "Goodness of Fit Models": goodness
        }
        
        estimated_value = ro.conversion.rpy2py(ro.globalenv['estimated_value'])
        mse = ro.conversion.rpy2py(ro.globalenv['mse'])
        vardir_var = ro.conversion.rpy2py(ro.globalenv['vardir_var'])
        estimated_value = estimated_value.flatten()
        vardir_var = vardir_var.to_numpy()[:, 0]
        rse = mse**0.5/estimated_value*100
        df = pl.DataFrame({
            'Eblup': estimated_value,
            'MSE': mse,
            'RSE (%)': rse})
        error = False
        return results, error, df
        
    except Exception as e:
        error = True
        return str(e), error, None