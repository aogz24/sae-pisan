from model.SaeModelling import SaeModelling
from service.modelling.running_model.SaeEblupPseudo import run_model_eblup_pseudo

class SaeEblupPseudo(SaeModelling):
    """
    SaeEblupPseudo is a class that extends SaeModelling to implement the EBLUP (Empirical Best Linear Unbiased Predictor) pseudo model.
    Methods
    -------
    __init__(*args, **kwargs)
        Initializes the SaeEblupPseudo instance with given arguments.
    run_model(r_script)
        Executes the EBLUP pseudo model using the provided R script.
        Parameters
        ----------
        r_script : str
            The R script to be executed.
        Returns
        -------
        result : Any
            The result of the model execution.
        error : Any
            Any error encountered during the model execution.
        df : pandas.DataFrame
            The dataframe resulting from the model execution.
    get_model2()
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
        result, error, df = run_model_eblup_pseudo(self)
        return result, error, df
    
    def get_model2(self):
        return self.model2