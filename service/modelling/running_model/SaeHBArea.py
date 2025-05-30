import polars as pl
from rpy2.rinterface_lib.embedded import RRuntimeError
from service.modelling.running_model.convert_df import convert_df
import os

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
        ro.r('datahb <- as.data.frame(r_df)')
        ro.r('attach(datahb)')
        try:
            ro.r(parent.r_script)  # Menjalankan skrip R
        except RRuntimeError as e:
            result = str(e)
            error = True
            return result, error, None
        
        from contextlib import contextmanager
        @contextmanager
        def png_device(filename, width=800, height=600, res=100):
            grdevices.png(file=filename, width=width, height=height, res=res)
            try:
                yield
            finally:
                grdevices.dev_off()
        
        script_png = """
        sae_autocorr <- function() {
            coda::autocorr.plot(modelhb$plot[[3]], col='brown2', lwd=2)
        }
        sae_plot <- function() {
            plot(modelhb$plot[[3]], col='brown2', lwd=2)
        }
        """
        
        ro.r(script_png)
        
        r_objects = ro.r("ls()")
        
        import rpy2.robjects.lib.grdevices as grdevices
        
        plots = [obj for obj in r_objects if obj.startswith("sae_")]

        temp_dir = os.path.join(os.getcwd(), "temp")
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        plot_paths = []

        for plot_name in plots:
            plot_path = os.path.join(temp_dir, f"{plot_name}.png")
            with png_device(plot_path):
                ro.r(f"{plot_name}()")
            plot_paths.append(plot_path)
        
        print("Saved plots:", plot_paths)
            
        ro.r('estimated_value_hb <- modelhb$Est')
        ro.r('sd_hb <- modelhb$sd')
        ro.r('refVar_hb <- modelhb$refVar')
        ro.r('coefficient_hb <- modelhb$coefficient')
        
        refvar = ro.globalenv['refVar_hb']
        refvar = int(float(refvar[0]))
        coefficient = ro.conversion.rpy2py(ro.globalenv['coefficient_hb'])
        coefficient.reset_index(inplace=True)
        coefficient.columns = ['Parameter'] + list(coefficient.columns[1:])
        coefficient = pl.DataFrame(coefficient)
        
        results ={
            "Model": "Hierarchical Bayesian",
            "Estimated Random Effect Variances": refvar,
            "Estimated Model Coefficient": coefficient,
        }
        estimated_value = ro.conversion.rpy2py(ro.globalenv['estimated_value_hb'])
        hb_mean = estimated_value["MEAN"]
        hb_25 = estimated_value["25%"]
        hb_50 = estimated_value["50%"]
        hb_75 = estimated_value["75%"]
        hb_97_5 = estimated_value["97.5%"]
        hb_sd = estimated_value["SD"]
        df = pl.DataFrame({
            'HB Mean': hb_mean,
            'HB 25%': hb_25,
            'HB 50%': hb_50,
            'HB 75%': hb_75,
            'HB 97.5%': hb_97_5,
            'Standard Deviation': hb_sd,})
        ro.r("detach(datahb)")
        
        error = False
        return results, error, df, plot_paths
        
    except Exception as e:
        error = True
        return str(e), error, None