from service.exploration.SummaryData import run_summary_data

class SummaryData:
    """
    A class used to represent the summary data model.
    Attributes
    ----------
    model1 : object
        The first model used in the summary data.
    model2 : object
        The second model used in the summary data.
    view : object
        The view associated with the summary data.
    result : str
        The result of the summary data processing.
    error : bool
        A flag indicating if there was an error during processing.
    Methods
    -------
    run_model(r_script)
        Executes the summary data model using the provided R script.
    activate_R()
        Activates the R environment for data processing using rpy2.
    """
    """
    Constructs all the necessary attributes for the SummaryData object.
    Parameters
    ----------
    model1 : object
        The first model used in the summary data.
    model2 : object
        The second model used in the summary data.
    view : object
        The view associated with the summary data.
    """
    """
    Executes the summary data model using the provided R script.
    Parameters
    ----------
    r_script : str
        The R script to be executed.
    """
    """
    Activates the R environment for data processing using rpy2.
    """
    
    def __init__(self, model1, model2):
        self.model1 = model1
        self.model2 = model2
        self.result = None
        self.error = False

    def run_model(self, r_script):
        self.r_script = r_script
        run_summary_data(self)

    def activate_R(self):
        from rpy2.robjects import pandas2ri
        pandas2ri.activate()