class SaeController:
    """
    Controller class for handling SAE model operations.
    Attributes:
        SAEmodel: An instance of the SAE model to be used for running scripts.
    Methods:
        __init__(SAEmodel):
            Initializes the SaeController with the given SAE model.
        run_model(r_script):
            Executes the given R script using the SAE model and returns the result, error, and dataframe.
    """
    """
    Initializes the SaeController with the given SAE model.
    Args:
        SAEmodel: An instance of the SAE model.
    """
    """
    Executes the given R script using the SAE model.
    Args:
        r_script (str): The R script to be executed.
    Returns:
        tuple: A tuple containing the result, error, and dataframe from the SAE model execution.
    """
    
    def __init__(self, SAEmodel):
        self.SAEmodel = SAEmodel
    
    def run_model(self, r_script):
        result, error, df = self.SAEmodel.run_model(r_script)
        return result, error, df