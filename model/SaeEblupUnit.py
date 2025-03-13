from model.SaeModelling import SaeModelling
from service.modelling.running_model.SaeEblupUnit import run_model_eblup_unit

class SaeEblupUnit(SaeModelling):
    """
    SaeEblupUnit is a class that extends SaeModelling to run EBLUP (Empirical Best Linear Unbiased Prediction) models.
    Methods
    -------
    __init__(*args, **kwargs)
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
        result, error, df = run_model_eblup_unit(self)
        return result, error, df
    
    def get_model2(self):
        return self.model2