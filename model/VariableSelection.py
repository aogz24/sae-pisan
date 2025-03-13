from service.exploration.VariableSelection import run_variable_selection

class VariableSelection:
    """
    A class used to represent the Variable Selection process.
    Attributes
    ----------
    model1 : object
        The first model used in the variable selection process.
    model2 : object
        The second model used in the variable selection process.
    view : object
        The view associated with the variable selection process.
    result : str
        The result of the variable selection process.
    error : bool
        A flag indicating if there was an error during the variable selection process.
    Methods
    -------
    run_model(r_script)
        Executes the variable selection process using the provided R script.
    activate_R()
        Activates the R environment using rpy2.
    """
    
    def __init__(self, model1, model2, view):
        self.model1 = model1
        self.model2 = model2
        self.view = view
        self.result =""
        self.error = False

    def run_model(self, r_script):
        self.r_script = r_script
        run_variable_selection(self)

    def activate_R(self):
        from rpy2.robjects import pandas2ri
        pandas2ri.activate()


