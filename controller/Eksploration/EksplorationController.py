class NormalityTestController:
    
    """
    Controller class for handling normality tests.
    This class is responsible for interfacing with the NormalityTestModel
    to run normality tests using provided R scripts.
    Attributes:
        NormalityTestModel: An instance of the NormalityTestModel class.
    Methods:
        __init__(NormalityTestModel):
            Initializes the NormalityTestController with the given model.
        run_model(r_script):
            Executes the normality test using the provided R script.
    """
    def __init__(self,NormalityTestModel):
        self.NormalityTestModel = NormalityTestModel

    def run_model(self, r_script):
        self.NormalityTestModel.run_model(r_script)

class SummaryDataController:
    """_summary_data_controller
    Controller class for handling summary data.
    This class is responsible for interfacing with the SummaryDataModel
    to generate summary data using provided R scripts.
    Attributes:
        SummaryData: An instance of the SummaryDataModel class.
    Methods:
        __init__(SummaryData):
            Initializes the SummaryDataController with the given model.
        run_model(r_script):
            Executes the summary data generation using the provided R script
    """
    def __init__(self, SummaryData):
        self.SummaryData = SummaryData
    
    def run_model(self, r_script):
        self.SummaryData.run_model(r_script)

class CorrelationMatrixController:
    """_summary_data_controller
    Controller class for handling correlation matrix.
    This class is responsible for interfacing with the CorrelationMatrixModel
    to generate correlation matrix using provided R scripts.
    Attributes:
        CorrelationMatrixModel: An instance of the CorrelationMatrixModel class.
    Methods:
        __init__(CorrelationMatrixModel):
            Initializes the CorrelationMatrixController with the given model.
        run_model(r_script):
            Executes the correlation matrix generation using the provided R script
    """
    def __init__(self, CorrelationMatrixModel):
        self.CorrelationMatrixModel = CorrelationMatrixModel
    
    def run_model(self, r_script):
        self.CorrelationMatrixModel.run_model(r_script)

class MulticollinearityController:
    """_summary_data_controller
    Controller class for handling multicollinearity.
    This class is responsible for interfacing with the MulticollinearityModel
    to generate multicollinearity using provided R scripts.
    Attributes:
        MulticollinearityModel: An instance of the MulticollinearityModel class.
    Methods:
        __init__(MulticollinearityModel):
            Initializes the MulticollinearityController with the given model.
        run_model(r_script):
    """
    def __init__(self, multicollinearityModel):
        self.MulticollinearityModel = multicollinearityModel
    
    def run_model(self, r_script):
        self.MulticollinearityModel.run_model(r_script)

class VariableSelectionController:
    """_summary_data_controller
    Controller class for handling variable selection.
    This class is responsible for interfacing with the VariableSelectionModel
    to generate variable selection using provided R scripts.
    Attributes:
        VariableSelectionModel: An instance of the VariableSelectionModel class.
    Methods:
        __init__(VariableSelectionModel):
            Initializes the VariableSelectionController with the given model.
        run_model(r_script):
            Executes the variable selection generation using the provided R
    """
    def __init__(self, VariableSelectionModel):
        self.VariableSelectionModel = VariableSelectionModel
    
    def run_model(self, r_script):
        self.VariableSelectionModel.run_model(r_script)
