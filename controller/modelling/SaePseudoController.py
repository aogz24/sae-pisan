class SaePseudoController:
    """
    A controller class for running SAE models using R scripts.
    Attributes:
        SAEmodel: An instance of the SAE model to be used.
    Methods:
        run_model(r_script):
            Executes the SAE model with the provided R script and returns the result, error, and dataframe.
    """
    """
    Initializes the SaePseudoController with the given SAE model.
    Args:
        SAEmodel: An instance of the SAE model to be used.
    """
    """
    Executes the SAE model with the provided R script.
    Args:
        r_script (str): The R script to be executed.
    Returns:
        tuple: A tuple containing the result, error, and dataframe from the model execution.
    """
    
    def __init__(self, SAEmodel):
        self.SAEmodel = SAEmodel
    
    def run_model(self, r_script):
        result, error, df = self.SAEmodel.run_model(r_script)
        return result, error, df