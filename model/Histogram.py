from service.graph.Histogram import run_histogram

class Histogram:
    """
    A class used to represent a Histogram model.
    Attributes
    ----------
    model1 : object
        The first model to be used in the histogram.
    model2 : object
        The second model to be used in the histogram.
    view : object
        The view associated with the histogram.
    plot : object, optional
        The plot object for the histogram (default is None).
    result : object, optional
        The result of the histogram computation (default is None).
    error : object, optional
        Any error encountered during the histogram computation (default is None).
    Methods
    -------
    run_model(r_script)
        Runs the histogram model using the provided R script.
    activate_R()
        Activates the R environment using rpy2's pandas2ri.
    """
    
    def __init__(self, model1, model2, view):
        self.model1 = model1
        self.model2 = model2
        self.view = view
        self.plot = None
        self.result = None
        self.error = None

    def run_model(self, r_script):
        self.r_script = r_script
        run_histogram(self)

    def activate_R(self):
        from rpy2.robjects import pandas2ri
        pandas2ri.activate()
    
