from model.SaeModelling import SaeModelling
from service.modelling.running_model.Projection import run_model_projection

class Projection(SaeModelling):
    """
    A class used to represent a Projection model which inherits from SaeModelling.
    Methods
    -------
    __init__(*args, **kwargs)
        Initializes the Projection model with given arguments.
    run_model(r_script)
        Executes the projection model using the provided R script.
        Parameters:
        r_script (str): The R script to be executed.
        Returns:
        tuple: A tuple containing the result, error, and dataframe from the model execution.
    get_model2()
        Retrieves the second model attribute.
        Returns:
        object: The second model attribute.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def run_model(self, r_script):
        self.r_script = r_script
        result, error, df = run_model_projection(self)
        return result, error, df
    
    def get_model2(self):
        return self.model2