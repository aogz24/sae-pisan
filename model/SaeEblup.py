from model.SaeModelling import SaeModelling
from service.modelling.running_model.SaeEblupArea import run_model_eblup_area

class SaeEblup(SaeModelling):
    """
    SaeEblup is a class that extends SaeModelling to run EBLUP (Empirical Best Linear Unbiased Prediction) models.
    Methods
    -------
    __init__(*args, **kwargs)
        Initializes the SaeEblup instance with given arguments.
    run_model(r_script)
        Executes the EBLUP model using the provided R script.
        Parameters:
        r_script (str): The R script to be executed.
        Returns:
        tuple: A tuple containing the result, error, and dataframe from the model execution.
    get_model2()
        Retrieves the model2 attribute.
        Returns:
        object: The model2 attribute.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def run_model(self, r_script):
        self.r_script = r_script
        result, error, df = run_model_eblup_area(self)
        return result, error, df
    
    def get_model2(self):
        return self.model2