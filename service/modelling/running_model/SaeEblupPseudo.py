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

    # Extract threshold information if available
    threshold_match = re.search(r"The threshold for the HCR and the PG is automatically set to (\d+)% of the median of the dependent variable and equals ([\d.]+)", output)
    if threshold_match:
        results['Threshold Percentage'] = int(threshold_match.group(1))
        results['Threshold Value'] = float(threshold_match.group(2))
    
    # Extract prediction information
    if "Empirical Best Prediction with sampling weights" in output:
        results['Prediction Method'] = "Empirical Best Prediction with sampling weights"

    # Extract out-of-sample and in-sample domains
    out_sample_match = re.search(r"Out-of-sample domains:\s+(\d+)", output)
    in_sample_match = re.search(r"In-sample domains:\s+(\d+)", output)
    
    # Alternative pattern from the image
    if not out_sample_match:
        out_sample_match = re.search(r"Out-of-sample domains:\s+(\d+)", output) or re.search(r"Out-of-sample domains:\s+(\d+)", output)
    
    if not in_sample_match:
        in_sample_match = re.search(r"In-sample domains:\s+(\d+)", output) or re.search(r"In-sample domains:\s+(\d+)", output)
    
    if out_sample_match:
        results['Out of sample domains'] = int(out_sample_match.group(1))
    if in_sample_match:
        results['In Sample domains'] = int(in_sample_match.group(1))

    # Extract transformation
    transformation_match = re.search(r"Transformation:\s+([\w\s]+)", output)
    if not transformation_match:
        transformation_match = re.search(r"Transformation:\s+([\w\s]+)", output)
    
    if transformation_match:
        results['Transformation'] = transformation_match.group(1).strip()

    # Extract model fit details if available
    model_fit_match = re.search(r"Model fit:(.*?)(?=\n\n|\Z)", output, re.DOTALL)
    if model_fit_match:
        results['Model Fit'] = model_fit_match.group(1).strip()
    
    # Extract fixed/list formula if available
    fixed_formula_match = re.search(r"where fixed/list\(fixed\) equals (.*?)(?=\n\n|\Z)", output, re.DOTALL)
    if fixed_formula_match:
        results['Fixed Formula'] = fixed_formula_match.group(1).strip()
    
    try:
        # Extract variance estimation method
        var_est_match = re.search(r"Variance estimation method:\s+([\w\s,]+)", output)
        if var_est_match:
            results['Variance Estimation Method'] = var_est_match.group(1).strip().split('\n')[0]
        
        # Extract k and mult_constant
        k_match = re.search(r"k\s+=\s+([\d.]+)", output)
        if k_match:
            results['k'] = float(k_match.group(1))
        
        mult_constant_match = re.search(r"mult_constant\s+=\s+([\d.]+)", output)
        if mult_constant_match:
            results['Mult constant'] = float(mult_constant_match.group(1))

        # Extract variance of random effects
        var_random_match = re.search(r"Variance of random effects:\s+([\d.]+)", output)
        if var_random_match:
            results['Variance of Random Effect'] = float(var_random_match.group(1))

        # Extract MSE method
        mse_method_match = re.search(r"MSE method:\s+([\w\s]+)", output)
        if mse_method_match:
            results['MSE Method'] = mse_method_match.group(1).strip().split('\n')[0]
    except:
        pass
        
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
        # Capture the model output first for better extraction
        # result_str = ro.r('capture.output(print(model_pseudo))')
        # result = "\n".join(result_str)
        # results = extract_output_results(result)
        
        # Get data from the model
        ro.r('estimated_value_pseudo <- getResponse(model_pseudo)\n mse_pseudo <- model_pseudo$MSE$FH \n domain_pseudo <-model_pseudo$MSE$Domain')
        domain = ro.conversion.rpy2py(ro.globalenv['domain_pseudo'])
        estimated_value = ro.conversion.rpy2py(ro.globalenv['estimated_value_pseudo'])
        mse = ro.conversion.rpy2py(ro.globalenv['mse_pseudo'])
        
        # Check if refVar exists in the model and get it safely
        try:
            ro.r('refvar_pseudo <- if(exists("model_pseudo$refVar")) model_pseudo$refVar else NULL')
            ro.r('vardir_var_pseudo <- if(exists("model_pseudo$vardir")) model_pseudo$vardir else matrix(0, nrow=length(domain_pseudo), ncol=1)')
            vardir_var = ro.conversion.rpy2py(ro.globalenv['vardir_var_pseudo'])
            vardir_var = vardir_var.to_numpy()[:, 0]
        except:
            vardir_var = [0] * len(domain)
            
        estimated_value = estimated_value.flatten()
        rse = abs(mse**0.5/estimated_value*100)
        df = pl.DataFrame({
            'Domain': domain,
            'Eblup': estimated_value,
            'MSE': mse,
            'RSE (%)': rse})
        error = False
        # Clean up R objects
        ro.r('rm(list=c("data_pseudo", "model_pseudo", "estimated_value_pseudo", "mse_pseudo", "domain_pseudo"), envir=globalenv())')
        ro.r('if(exists("refvar_pseudo")) rm(refvar_pseudo, envir=globalenv())')
        ro.r('if(exists("vardir_var_pseudo")) rm(vardir_var_pseudo, envir=globalenv())')
        ro.r("gc()")  # Clear R memory
        return None, error, df
        
    except Exception as e:
        if hasattr(parent, 'log_exception'):
            parent.log_exception(e, "Run Model EBLUP Pseudo")
        error = True
        return str(e), error, None