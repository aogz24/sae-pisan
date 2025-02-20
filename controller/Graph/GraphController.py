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

class HistogramController:
    def __init__(self, HistogramModel):
        self.HistogramModel = HistogramModel
    
    def run_model(self, r_script):
        self.HistogramModel.run_model(r_script)