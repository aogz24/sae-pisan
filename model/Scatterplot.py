from service.graph.Scatterplot import run_scatterplot

class Scatterplot:
    """
    A class used to represent a Scatterplot model.
    Attributes
    ----------
    model1 : object
        The first model to be used in the scatterplot.
    model2 : object
        The second model to be used in the scatterplot.
    view : object
        The view associated with the scatterplot.
    plot : object, optional
        The plot object, initialized as None.
    error : object, optional
        The error object, initialized as None.
    result : object, optional
        The result object, initialized as None.
    Methods
    -------
    run_model(r_script)
        Runs the scatterplot model using the provided R script.
    activate_R()
        Activates the R environment using rpy2's pandas2ri.
    """
    """
    Constructs all the necessary attributes for the Scatterplot object.
    Parameters
    ----------
    model1 : object
        The first model to be used in the scatterplot.
    model2 : object
        The second model to be used in the scatterplot.
    view : object
        The view associated with the scatterplot.
    """
    """
    Runs the scatterplot model using the provided R script.
    Parameters
    ----------
    r_script : str
        The R script to be used for running the scatterplot model.
    """
    """
    Activates the R environment using rpy2's pandas2ri.
    """
    
    def __init__(self, model1, model2, view):
        self.model1 = model1
        self.model2 = model2
        self.view = view
        self.plot = None
        self.error = None
        self.result = None

    def run_model(self, r_script):
        self.r_script = r_script
        run_scatterplot(self)

    def activate_R(self):
        from rpy2.robjects import pandas2ri
        pandas2ri.activate()
    
