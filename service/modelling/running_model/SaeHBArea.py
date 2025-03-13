import polars as pl
from rpy2.rinterface_lib.embedded import RRuntimeError
from service.modelling.running_model.convert_df import convert_df

def run_model_hb_area(parent):
    """
    Runs the hierarchical Bayesian area model using the provided parent object.
    This function activates the R environment, processes the data, and runs the specified R script
    to perform hierarchical Bayesian modeling. It captures the results and returns them along with
    any errors encountered during execution.
    Parameters:
    parent (object): An object that contains the necessary methods and attributes for running the model.
                     It should have the following methods and attributes:
                     - activate_R(): Method to activate the R environment.
                     - model1.get_data(): Method to get the data for modeling.
                     - r_script: A string containing the R script to be executed.
    Returns:
    tuple: A tuple containing:
           - result_str (str): A string with the formatted results of the model.
           - error (bool): A boolean indicating whether an error occurred.
           - df (polars.DataFrame or None): A DataFrame containing the estimated values and standard deviations,
                                            or None if an error occurred.
    """
    
    import rpy2.robjects as ro
    parent.activate_R()
    df = parent.model1.get_data()
    df = df.drop_nulls()
    convert_df(df, parent)
    result = ""
    error = False
    try:
        ro.r('suppressMessages(library(saeHB))')
        ro.r('data <- as.data.frame(r_df)')
        ro.r('attach(data)')
        try:
            ro.r(parent.r_script)  # Menjalankan skrip R
        except RRuntimeError as e:
            result = str(e)
            error = True
            return result, error, None
        ro.r('estimated_value <- model$Est')
        ro.r('sd <- model$sd')
        ro.r('refVar <- model$refVar')
        ro.r('coefficient <- model$coefficient')
        
        result_str = "Estimated Value:\n" + "\n".join(ro.r('capture.output(print(estimated_value))')) + "\n\n"
        result_str += "Standard Deviation:\n" + "\n".join(ro.r('capture.output(print(sd))')) + "\n\n"
        result_str += "Reference Variance:\n" + "\n".join(ro.r('capture.output(print(refVar))')) + "\n\n"
        result_str += "Coefficient:\n" + "\n".join(ro.r('capture.output(print(coefficient))')) + "\n"
        estimated_value = ro.conversion.rpy2py(ro.globalenv['estimated_value'])
        hb_mean = estimated_value["MEAN"]
        hb_25 = estimated_value["25%"]
        hb_50 = estimated_value["50%"]
        hb_75 = estimated_value["75%"]
        hb_97_5 = estimated_value["97.5%"]
        hb_sd = estimated_value["SD"]
        df = pl.DataFrame({
            'HB_Mean': hb_mean,
            'HB_25%': hb_25,
            'HB_50%': hb_50,
            'HB_75%': hb_75,
            'HB_97.5%': hb_97_5,
            'SD': hb_sd,})
        ro.r("detach(data)")
        
        error = False
        return result_str, error, df
        
    except Exception as e:
        error = True
        return str(e), error, None