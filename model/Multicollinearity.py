from service.exploration.Multicollinearity import run_multicollinearity

class Multicollinearity:
    """
    A class to handle multicollinearity analysis using R scripts.
    Attributes
    ----------
    model1 : object
        The first model to be analyzed.
    model2 : object
        The second model to be analyzed.
    view : object
        The view component for displaying results.
    result : str
        The result of the multicollinearity analysis.
    reg_model : bool
        A flag indicating if the regression model is set.
    error : bool
        A flag indicating if there was an error during analysis.
    Methods
    -------
    __init__(model1, model2, view)
        Initializes the Multicollinearity class with the given models and view.
    run_model(r_script)
        Runs the multicollinearity analysis using the provided R script.
    activate_R()
        Activates the R environment for running R scripts.
    """
    
    def __init__(self, model1, model2):
        self.model1 = model1
        self.model2 = model2
        self.result =""
        self.reg_model = False
        self.error = False

    def run_model(self, r_script):
        self.r_script = r_script
        run_multicollinearity(self)

    def activate_R(self):
        from rpy2.robjects import pandas2ri
        pandas2ri.activate()