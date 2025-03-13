class SaeEblupUnitController:
    """
    Controller class for running Small Area Estimation (SAE) models using EBLUP (Empirical Best Linear Unbiased Prediction).
    Attributes:
        SAEmodel: An instance of a class that provides the `run_model` method to execute the SAE model.
    Methods:
        __init__(SAEmodel):
            Initializes the SaeEblupUnitController with the given SAE model instance.
        run_model(r_script):
            Executes the SAE model using the provided R script.
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