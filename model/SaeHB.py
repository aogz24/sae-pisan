from model.SaeModelling import SaeModelling
from service.modelling.running_model.SaeHBArea import run_model_hb_area

class SaeHB(SaeModelling):
    """
    SaeHB class that extends SaeModelling to run hierarchical Bayesian models.
    Methods
    -------
    __init__(*args, **kwargs)
        Initializes the SaeHB class with given arguments.
    run_model(r_script)
        Runs the hierarchical Bayesian model using the provided R script.
    get_model2()
        Returns the model2 attribute.
    """
    """
    Initializes the SaeHB class with given arguments.
    Parameters
    ----------
    *args : tuple
        Variable length argument list.
    **kwargs : dict
        Arbitrary keyword arguments.
    """
    """
    Runs the hierarchical Bayesian model using the provided R script.
    Parameters
    ----------
    r_script : str
        The R script to be used for running the model.
    Returns
    -------
    result : Any
        The result of the model run.
    error : Any
        Any error encountered during the model run.
    df : pandas.DataFrame
        The dataframe resulting from the model run.
    """
    """
    Returns the model2 attribute.
    Returns
    -------
    Any
        The model2 attribute.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def run_model(self, r_script):
        self.r_script = r_script
        result, error, df = run_model_hb_area(self)
        return result, error, df
    
    def get_model2(self):
        return self.model2