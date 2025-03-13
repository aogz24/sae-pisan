class SaeModelling:
    """
    A class used to represent the SAE Modelling.
    Attributes
    ----------
    model1 : object
        The first model used in the SAE Modelling.
    model2 : object
        The second model used in the SAE Modelling.
    view : object
        The view associated with the SAE Modelling.
    error : bool
        A flag indicating if there is an error in the SAE Modelling.
    Methods
    -------
    activate_R():
        Activates the R environment for use with pandas dataframes.
    """
    
    def __init__(self, model1, model2, view):
        self.model1 = model1
        self.model2 = model2
        self.view = view
        self.error = False
        
    def activate_R(self):
        from rpy2.robjects import pandas2ri
        pandas2ri.activate()