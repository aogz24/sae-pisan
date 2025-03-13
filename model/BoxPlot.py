from service.graph.BoxPlot import run_box_plot

class BoxPlot:
    """
    A class used to represent a BoxPlot.
    Attributes
    ----------
    model1 : object
        The first model to be used in the box plot.
    model2 : object
        The second model to be used in the box plot.
    view : object
        The view associated with the box plot.
    plot : object, optional
        The plot object, initialized as None.
    result : object, optional
        The result of the box plot, initialized as None.
    error : bool, optional
        A flag indicating if there was an error, initialized as False.
    Methods
    -------
    run_model(r_script)
        Runs the box plot model using the provided R script.
    activate_R()
        Activates the R environment using rpy2.
    """
    
    def __init__(self, model1, model2, view):
        self.model1 = model1
        self.model2 = model2
        self.view = view
        self.plot = None
        self.result = None
        self.error = False

    def run_model(self, r_script):
        self.r_script = r_script
        run_box_plot(self)

    def activate_R(self):
        from rpy2.robjects import pandas2ri
        pandas2ri.activate()
    
