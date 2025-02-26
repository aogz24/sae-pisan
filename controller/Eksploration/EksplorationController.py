class NormalityTestController:
    def __init__(self,NormalityTestModel):
        self.NormalityTestModel = NormalityTestModel

    def run_model(self, r_script):
        self.NormalityTestModel.run_model(r_script)

class SummaryDataController:
    def __init__(self, SummaryData):
        self.SummaryData = SummaryData
    
    def run_model(self, r_script):
        self.SummaryData.run_model(r_script)

class CorrelationMatrixController:
    def __init__(self, CorrelationMatrixModel):
        self.CorrelationMatrixModel = CorrelationMatrixModel
    
    def run_model(self, r_script):
        self.CorrelationMatrixModel.run_model(r_script)

class MulticollinearityController:
    def __init__(self, multicollinearityModel):
        self.MulticollinearityModel = multicollinearityModel
    
    def run_model(self, r_script):
        self.MulticollinearityModel.run_model(r_script)

class VariableSelectionController:
    def __init__(self, VariableSelectionModel):
        self.VariableSelectionModel = VariableSelectionModel
    
    def run_model(self, r_script):
        self.VariableSelectionModel.run_model(r_script)
