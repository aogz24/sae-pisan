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
    df = parent.model1.get_data()
    df = df.drop_nulls()
    convert_df(df, parent)
    result = ""
    error = False
    try:
        from rpy2.robjects.packages import importr
        importr('saeHB')
        ro.r('datahb <- as.data.frame(r_df)')
        ro.r('attach(datahb)')
        try:
            ro.r(parent.r_script)  # Menjalankan skrip R
        except RRuntimeError as e:
            if hasattr(parent, 'log_exception'):
                parent.log_exception(e, "Run Model Hierarchical Bayesian Area")
            result = str(e)
            error = True
            return result, error, None, None
        
        from contextlib import contextmanager
        import rpy2.robjects.lib.grdevices as grdevices
        @contextmanager
        def png_device(filename, width=800, height=600, res=100):
            grdevices.png(file=filename, width=width, height=height, res=res)
            try:
                yield
            finally:
                grdevices.dev_off()
        
        script_png = """
        # Import required libraries
        library(coda)
        
        # Get the MCMC samples for plotting (similar to Normal.R)
        result_mcmc <- modelhb$plot[[length(modelhb$plot)-1]]
        
        # Get parameter names for individual plots
        param_names <- colnames(result_mcmc[[1]])
        n_params <- length(param_names)
        
        sae_autocorr <- function(param_idx = NULL) {
            if (is.null(param_idx)) {
                coda::autocorr.plot(result_mcmc, col='brown2', lwd=2)
            } else {
                coda::autocorr.plot(result_mcmc[,param_idx], col='brown2', lwd=2, 
                                    main=paste("Autocorrelation -", param_names[param_idx]))
            }
        }

        sae_trace_density <- function(param_idx = NULL) {
            if (is.null(param_idx)) {
                plot(result_mcmc, col='brown2', lwd=2)
            } else {
                plot(result_mcmc[,param_idx], col='brown2', lwd=2,
                        main=paste("Trace and Density -", param_names[param_idx]))
            }
        }
        """
        
        ro.r(script_png)
        
        # Create temp directory for plots
        temp_dir = os.path.join(os.getcwd(), "temp")
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        
        plot_paths = []
        
        # Get number of parameters
        n_params = ro.r("length(param_names)")[0]
        param_names = ro.r("param_names")
        
        # Generate autocorrelation plots - all parameters in one plot
        autocorr_path = os.path.join(temp_dir, "sae_autocorr_all_plot.png")
        try:
            grdevices.dev_off()
        except:
            pass
        
        grdevices.png(file=autocorr_path, width=1200, height=800, res=100)
        try:
            ro.r("sae_autocorr()")
            plot_paths.append(autocorr_path)
        except Exception as e:
            print(f"Error creating autocorrelation plot (all): {e}")
        finally:
            try:
                grdevices.dev_off()
            except:
                pass
        
        # Generate individual autocorrelation plots for each parameter
        for i in range(int(n_params)):
            param_name = param_names[i].replace("[", "_").replace("]", "")
            autocorr_param_path = os.path.join(temp_dir, f"sae_autocorr_{param_name}_plot.png")
            try:
                grdevices.dev_off()
            except:
                pass
            
            grdevices.png(file=autocorr_param_path, width=800, height=600, res=100)
            try:
                ro.r(f"sae_autocorr({i+1})")
                plot_paths.append(autocorr_param_path)
            except Exception as e:
                print(f"Error creating autocorrelation plot for {param_name}: {e}")
            finally:
                try:
                    grdevices.dev_off()
                except:
                    pass
        
        # Generate trace and density plots - all parameters in one plot
        trace_density_path = os.path.join(temp_dir, "sae_trace_density_all_plot.png")
        try:
            grdevices.dev_off()
        except:
            pass
            
        grdevices.png(file=trace_density_path, width=1200, height=800, res=100)
        try:
            ro.r("sae_trace_density()")
            plot_paths.append(trace_density_path)
        except Exception as e:
            print(f"Error creating trace/density plot (all): {e}")
        finally:
            try:
                grdevices.dev_off()
            except:
                pass
        
        # Generate individual trace and density plots for each parameter
        for i in range(int(n_params)):
            param_name = param_names[i].replace("[", "_").replace("]", "")
            trace_param_path = os.path.join(temp_dir, f"sae_trace_density_{param_name}_plot.png")
            try:
                grdevices.dev_off()
            except:
                pass
            
            grdevices.png(file=trace_param_path, width=800, height=600, res=100)
            try:
                ro.r(f"sae_trace_density({i+1})")
                plot_paths.append(trace_param_path)
            except Exception as e:
                print(f"Error creating trace/density plot for {param_name}: {e}")
            finally:
                try:
                    grdevices.dev_off()
                except:
                    pass
        
            
        ro.r('estimated_value_hb <- modelhb$Est')
        ro.r('sd_hb <- modelhb$sd')
        ro.r('refVar_hb <- modelhb$refVar')
        ro.r('coefficient_hb <- modelhb$coefficient')
        
        refvar = ro.globalenv['refVar_hb']
        refvar = str(float(refvar[0]))
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
        rse = abs(hb_sd / hb_mean ) * 100
        df = pl.DataFrame({
            'HB Mean': hb_mean,
            'HB 25%': hb_25,
            'HB 50%': hb_50,
            'HB 75%': hb_75,
            'HB 97.5%': hb_97_5,
            'Standard Deviation': hb_sd,
            'RSE': rse
        })
        ro.r("detach(datahb)")
        ro.r("rm(datahb)")
        ro.r("rm(modelhb)")
        ro.r("gc()")
        
        error = False
        return results, error, df, plot_paths
        
    except Exception as e:
        if hasattr(parent, 'log_exception'):
            parent.log_exception(e, "Run Model Hierarchical Bayesian Area")
        error = True
        return str(e), error, None, None