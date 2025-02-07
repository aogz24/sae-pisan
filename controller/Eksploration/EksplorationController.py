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

class ScatterPlotController:
    def __init__(self, ScatterPlotModel):
        self.ScatterPlotModel = ScatterPlotModel
    
    def run_model(self, r_script):
        self.ScatterPlotModel.run_model(r_script)

class LinePlotController:
    def __init__(self, LinePlotModel):
        self.LinePlotModel = LinePlotModel
    
    def run_model(self, r_script):
        self.LinePlotModel.run_model(r_script)

class BoxPlotController:
    def __init__(self, BoxPlotModel):
        self.BoxPlotModel = BoxPlotModel
    
    def run_model(self, r_script):
        self.BoxPlotModel.run_model(r_script)

class CorrelationMatrixController:
    def __init__(self, CorrelationMatrixModel):
        self.CorrelationMatrixModel = CorrelationMatrixModel
    
    def run_model(self, r_script):
        self.CorrelationMatrixModel.run_model(r_script)