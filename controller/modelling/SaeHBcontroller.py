class SaeHBController:
    """
    Controller class for handling SAE model operations.
    Attributes:
        SAEmodel: An instance of the SAE model to be controlled.
    """
    """
    Initializes the SaeHBController with the given SAE model.
    Args:
        SAEmodel: The SAE model instance to be used by the controller.
    """
    """
    Runs the SAE model using the provided R script.
    Args:
        r_script (str): The R script to be executed by the SAE model.
    Returns:
        tuple: A tuple containing the result, error, and dataframe (df) from the model execution.
    """
    
    def __init__(self, SAEmodel):
        self.SAEmodel = SAEmodel
    
    def run_model(self, r_script):
        result, error, df = self.SAEmodel.run_model(r_script)
        return result, error, df