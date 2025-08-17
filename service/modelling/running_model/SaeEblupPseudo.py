import polars as pl
from PyQt6.QtWidgets import QMessageBox
from rpy2.rinterface_lib.embedded import RRuntimeError
from service.modelling.running_model.convert_df import convert_df


def extract_output_results(output):
    """
    Extracts results from the given output string and returns it as a dictionary.
    """
    import re
    import polars as pl
    results = {}
    
    # Extract model type
    if "Empirical Best Prediction" in output:
        results['Model'] = 'Empirical Best Prediction'
    else:
        results['Model'] = 'Pseudo Empirical Best Linear Unbiased Prediction (Fay-Herriot)'

    # Extract Call/Formula
    call_match = re.search(r"Call:[\s\n]+ebp\(fixed = (.*?)(?=,|\))", output, re.DOTALL)
    if call_match:
        results['Call'] = call_match.group(1).strip()
    
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
    
    if out_sample_match:
        results['Out of sample domains'] = int(out_sample_match.group(1))
    if in_sample_match:
        results['In Sample domains'] = int(in_sample_match.group(1))

    # Extract sample sizes
    units_sample_match = re.search(r"Units in sample:\s+(\d+)", output)
    units_pop_match = re.search(r"Units in population:\s+(\d+)", output)
    
    if units_sample_match:
        results['Units in sample'] = int(units_sample_match.group(1))
    if units_pop_match:
        results['Units in population'] = int(units_pop_match.group(1))
    
    # Extract domain statistics (from the table in the image)
    # This is complex data, might need to store it as text or parse into a structure
    domains_stats_match = re.search(r"Sample_domains\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)", output)
    pop_domains_match = re.search(r"Population_domains\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)", output)
    
    if domains_stats_match:
        results['Sample_domains'] = {
            'Min': float(domains_stats_match.group(1)),
            '1st Qu': float(domains_stats_match.group(2)),
            'Median': float(domains_stats_match.group(3)),
            'Mean': float(domains_stats_match.group(4)),
            '3rd Qu': float(domains_stats_match.group(5)),
            'Max': float(domains_stats_match.group(6))
        }
    
    if pop_domains_match:
        results['Population_domains'] = {
            'Min': float(pop_domains_match.group(1)),
            '1st Qu': float(pop_domains_match.group(2)),
            'Median': float(pop_domains_match.group(3)),
            'Mean': float(pop_domains_match.group(4)),
            '3rd Qu': float(pop_domains_match.group(5)),
            'Max': float(pop_domains_match.group(6))
        }

    # Extract ICC value
    icc_match = re.search(r"ICC:\s+([\d.]+)", output)
    if icc_match:
        results['ICC'] = float(icc_match.group(1))

    # Extract transformation
    transformation_match = re.search(r"Transformation:\s+([\w\s]+)", output)
    if transformation_match:
        results['Transformation'] = transformation_match.group(1).strip()

    # Extract explanatory measures
    if "Explanatory measures for the mixed model" in output:
        results['Has Explanatory Measures'] = True
    
    # Extract residual diagnostics
    if "Residual diagnostics for the mixed model" in output:
        results['Has Residual Diagnostics'] = True

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
        result_str = ro.r('capture.output(summary(model_pseudo))')
        result = "\n".join(result_str)
        results = extract_output_results(result)
        

        # Get data from the model
        ro.r('estimated_value_pseudo <- predict(model_pseudo)\n mse_pseudo <- model_pseudo$MSE$Mean \n domain_pseudo <-model_pseudo$MSE$Domain \n estimator<-estimators(model_pseudo) \n varcof <- getVarCov.ebp(model_pseudo)')
        import pandas as pd
        import numpy as np
        
        # More direct approach to get the estimator data
        # Use R to convert the estimator to a proper data frame first
        ro.r('''
        # Ensure estimator is a proper data frame
        if(is.list(estimator) && !is.data.frame(estimator)) {
          # If it's a list with components like 'ind', extract the data frame
          if("ind" %in% names(estimator) && is.data.frame(estimator$ind)) {
            estimator <- estimator$ind
          }
        }
        # Make sure all columns have proper names
        if(is.data.frame(estimator)) {
          names(estimator) <- make.names(names(estimator))
        }
        ''')
        
        # Now convert to Python
        estimator_raw = ro.conversion.rpy2py(ro.globalenv['estimator'])
        print("Estimator raw:", type(estimator_raw))
        
        # Handle direct conversion
        if isinstance(estimator_raw, pd.DataFrame):
            estimator = estimator_raw
        else:
            # If it's not already a DataFrame, create one
            try:
                estimator = pd.DataFrame(estimator_raw)
            except Exception as e:
                print(f"Error converting to DataFrame: {e}")
                # Create an empty DataFrame as fallback
                estimator = pd.DataFrame()
        
        # Convert all object and category columns to string to avoid polars conversion errors
        for col in estimator.columns:
            if estimator[col].dtype.name in ['category', 'object'] or str(estimator[col].dtype).startswith('category'):
                estimator[col] = estimator[col].astype(str)
        
        # Convert to polars DataFrame
        estimator_df = pl.from_pandas(estimator)
        results["Estimators"] = estimator_df
        
        random_effect_variance = ro.globalenv['varcof']
        # Convert numpy ndarray to float if possible
        if isinstance(random_effect_variance, np.ndarray) and random_effect_variance.size == 1:
            random_effect_variance = float(random_effect_variance.item())
        results["Random Effect Variance"] = random_effect_variance

        mse = ro.conversion.rpy2py(ro.globalenv['mse_pseudo'])
        estimated_value = ro.conversion.rpy2py(ro.globalenv['estimated_value_pseudo'])

        # estimated_value is a pandas DataFrame, convert to polars DataFrame
        df = pl.from_pandas(estimated_value)
        
        df = df.with_columns([
            pl.Series('MSE', mse)
        ])
        
        if 'Mean' in df.columns:
            df = df.with_columns(
            (df['MSE'] ** 0.5 / df['Mean'] * 100).abs().alias('RSE (%)')
            )
        error = False
        # Clean up R objects
        ro.r('rm(list=c("data_pseudo", "model_pseudo", "estimated_value_pseudo", "mse_pseudo", "domain_pseudo"), envir=globalenv())')
        ro.r('if(exists("refvar_pseudo")) rm(refvar_pseudo, envir=globalenv())')
        ro.r('if(exists("vardir_var_pseudo")) rm(vardir_var_pseudo, envir=globalenv())')
        ro.r("gc()")  # Clear R memory
        return results, error, df
        
    except Exception as e:
        if hasattr(parent, 'log_exception'):
            parent.log_exception(e, "Run Model EBLUP Pseudo")
        error = True
        return str(e), error, None