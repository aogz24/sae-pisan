from service.graph.Lineplot import run_lineplot

class Lineplot:
    """
    A class used to represent a Line Plot.
    Attributes
    ----------
    model1 : object
        The first model to be used in the line plot.
    model2 : object
        The second model to be used in the line plot.
    view : object
        The view associated with the line plot.
    plot : object, optional
        The plot object, initialized as None.
    error : bool
        A flag indicating if there was an error, initialized as False.
    result : object, optional
        The result of the line plot, initialized as None.
    Methods
    -------
    __init__(model1, model2, view)
        Initializes the Lineplot with the given models and view.
    run_model(r_script)
        Runs the line plot model using the provided R script.
    activate_R()
        Activates the R environment using rpy2.
    """
    
    def __init__(self, model1, model2, view):
        self.model1 = model1
        self.model2 = model2
        self.view = view
        self.plot = None
        self.error = False
        self.result = None

    def run_model(self, r_script):
        self.r_script = r_script
        run_lineplot(self)

    def activate_R(self):
        from rpy2.robjects import pandas2ri
        pandas2ri.activate()
    
