import polars as pl
from PyQt6.QtWidgets import QMessageBox
from rpy2.rinterface_lib.embedded import RRuntimeError
from service.modelling.running_model.convert_df import convert_df


def extract_output_results(output):
    """
    Extracts results from the given output string and returns it as a dictionary.
    """
    import re
    results = {}
    
    results['Model'] = 'Pseudo Empirical Best Linear Unbiased Prediction (Fay-Herriot)'

    # Extract out-of-sample and in-sample domains
    results['Out of sample domains'] = int(re.search(r"Out-of-sample domains:\s+(\d+)", output).group(1))
    results['In Sample domains'] = int(re.search(r"In-sample domains:\s+(\d+)", output).group(1))

    # Extract variance estimation method
    results['Variance Estimation Method'] = re.search(r"Variance estimation method:\s+([\w\s,]+)", output).group(1).strip().split('\n')[0]
    
    # Extract k and mult_constant
    results['k'] = float(re.search(r"k\s+=\s+([\d.]+)", output).group(1))
    results['Mult constant'] = float(re.search(r"mult_constant\s+=\s+([\d.]+)", output).group(1))

    # Extract variance of random effects
    results['Variance of Random Effect'] = float(re.search(r"Variance of random effects:\s+([\d.]+)", output).group(1))

    # Extract MSE method
    results['MSE Method'] = re.search(r"MSE method:\s+([\w\s]+)", output).group(1).strip().split('\n')[0]
    
    # Extract transformation
    results['Transformation'] = re.search(r"Transformation:\s+([\w\s]+)", output).group(1).strip()

    return results

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
    df = df.filter(~pl.all_horizontal(pl.all().is_null()))
    convert_df(df, parent)
    result = ""
    error = False
    try:
        ro.r('data_pseudo <- as.data.frame(r_df)')
        try:
            ro.r(parent.r_script)  # Menjalankan skrip R
        except RRuntimeError as e:
            if hasattr(parent, 'log_exception'):
                parent.log_exception(e, "Run Model EBLUP Pseudo")
            result = str(e)
            error = True
            return result, error, None
        ro.r('estimated_value_pseudo <- getResponse(model_pseudo)\n mse_pseudo <- model_pseudo$MSE$FH \n domain_pseudo <-model_pseudo$MSE$Domain \n refvar_pseudo <-model_pseudo$refVar')
        domain = ro.conversion.rpy2py(ro.globalenv['domain_pseudo'])
        result_str = ro.r('capture.output(print(model_pseudo))')
        result = "\n".join(result_str)
        results = extract_output_results(result)
        estimated_value = ro.conversion.rpy2py(ro.globalenv['estimated_value_pseudo'])
        mse = ro.conversion.rpy2py(ro.globalenv['mse_pseudo'])
        vardir_var = ro.conversion.rpy2py(ro.globalenv['vardir_var_pseudo'])
        estimated_value = estimated_value.flatten()
        vardir_var = vardir_var.to_numpy()[:, 0]
        rse = abs(mse**0.5/estimated_value*100)
        df = pl.DataFrame({
            'Domain': domain,
            'Eblup': estimated_value,
            'MSE': mse,
            'RSE (%)': rse})
        error = False
        return results, error, df
        
    except Exception as e:
        if hasattr(parent, 'log_exception'):
            parent.log_exception(e, "Run Model EBLUP Pseudo")
        error = True
        return str(e), error, None