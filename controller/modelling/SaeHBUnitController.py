class SaeHBUnitController:
    """
    Controller class for running Small Area Estimation (SAE) models using HB (Hierarchical Bayes).
    Attributes:
        SAEmodel: An instance of a class that provides the `run_model` method to execute the SAE model.
    Methods:
        __init__(SAEmodel):
            Initializes the SaeHBUnitController with the given SAE model instance.
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
        results, error, df, plot_path = self.SAEmodel.run_model(r_script)
        return results, error, df, plot_path