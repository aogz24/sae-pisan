from service.exploration.NormalityTest import run_normality_test

class NormalityTest:
    """
    A class used to perform normality tests on given models and selected columns.
    Attributes
    ----------
    model1 : object
        The first model to be tested.
    model2 : object
        The second model to be tested.
    selected_columns : list
        The columns selected for the normality test.
    view : object
        The view associated with the normality test.
    result : str
        The result of the normality test.
    plot : object
        The plot generated from the normality test.
    error : bool
        A flag indicating if there was an error during the normality test.
    Methods
    -------
    run_model(r_script)
        Runs the normality test using the provided R script.
    activate_R()
        Activates the R environment for running the normality test.
    """
    
    def __init__(self, model1, model2, selected_columns, view):
        self.model1 = model1
        self.model2 = model2
        self.view = view
        self.selected_columns = selected_columns
        self.result =""
        self.plot = None
        self.error = False

    def run_model(self, r_script):
        self.r_script = r_script
        run_normality_test(self)

    def activate_R(self):
        from rpy2.robjects import pandas2ri
        pandas2ri.activate()
    
