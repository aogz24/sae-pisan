class ProjectionController:
    """
    Controller class for handling projection model operations.
    Attributes:
        projectionModel: An instance of the projection model to be used.
    Methods:
        run_model(r_script):
            Executes the projection model with the provided R script.
            Args:
                r_script (str): The R script to be executed by the projection model.
            Returns:
                tuple: A tuple containing the result, error, and dataframe from the model execution.
    """
    
    def __init__(self, projectionModel):
        self.projectionModel = projectionModel
    
    def run_model(self, r_script):
        result, error, df = self.projectionModel.run_model(r_script)
        return result, error, df