from model.SaeModelling import SaeModelling
from service.modelling.running_model.SaeHBUnit import run_model_hb_unit

class SaeHBUnit(SaeModelling):
    """
    SaeHBUnit is a class that extends SaeModelling to run HB (Hierarchical Bayes) models.
    Methods
    -------
    __init__(*args, **kwargs)
        Initializes the SaeHBUnit instance with given arguments.
        Initializes the SaeEblupUnit instance with given arguments.
    run_model(r_script)
        Runs the EBLUP model using the provided R script.
        Parameters
        ----------
        r_script : str
            The R script to be executed for running the EBLUP model.
        Returns
        -------
        result : Any
            The result of the EBLUP model execution.
        error : Any
            Any error encountered during the model execution.
        df : pandas.DataFrame
            The dataframe containing the results of the model execution.
    get_model2()
        Returns the model2 attribute.
        Returns
        -------
        model2 : Any
            The model2 attribute of the instance.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def run_model(self, r_script):
        self.r_script = r_script
        results, error, df, plot_paths = run_model_hb_unit(self)
        return results, error, df, plot_paths
    
    def get_model2(self):
        return self.model2