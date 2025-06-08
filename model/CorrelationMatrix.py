from service.exploration.CorrelationMatrix import run_correlation_matrix

class CorrelationMatrix:
    """
    A class to represent a correlation matrix model.
    Attributes
    ----------
    model1 : object
        The first model to be used in the correlation matrix.
    model2 : object
        The second model to be used in the correlation matrix.
    view : object
        The view associated with the correlation matrix.
    result : str
        The result of the correlation matrix computation.
    plot : object, optional
        The plot of the correlation matrix (default is None).
    error : bool
        A flag indicating if there was an error during computation (default is False).
    Methods
    -------
    run_model(r_script):
        Runs the correlation matrix model using the provided R script.
    activate_R():
        Activates the R environment using rpy2.
    """
    
    def __init__(self, model1, model2):
        self.model1 = model1
        self.model2 = model2
        self.result =""
        self.plot = None
        self.error = False

    def run_model(self, r_script):
        self.r_script = r_script
        run_correlation_matrix(self)

    def activate_R(self):
        from rpy2.robjects import pandas2ri
        pandas2ri.activate()
    
