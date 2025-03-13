class ScatterPlotController:
    """_summary_scatter_plot_controller_
    This class is responsible for controlling the ScatterPlotModel.
    Attributes:
        ScatterPlotModel (ScatterPlotModel): An instance of the ScatterPlotModel class.
    Methods:
        __init__(ScatterPlotModel):
            Initializes the ScatterPlotController with a ScatterPlotModel instance.
        run_model(r_script):
            Executes the run_model method of the ScatterPlotModel with the provided R script.
    """
    def __init__(self, ScatterPlotModel):
        self.ScatterPlotModel = ScatterPlotModel
    
    def run_model(self, r_script):
        self.ScatterPlotModel.run_model(r_script)

class LinePlotController:
    """_summary_line_plot_controller_
    This class is responsible for controlling the LinePlotModel.
    Attributes:
        LinePlotModel (LinePlotModel): An instance of the LinePlotModel class.
    Methods:
        __init__(LinePlotModel):
            Initializes the LinePlotController with a LinePlotModel instance.
        run_model(r_script):
            Executes the run_model method of the LinePlotModel with the provided R script.
    """
    def __init__(self, LinePlotModel):
        self.LinePlotModel = LinePlotModel
    
    def run_model(self, r_script):
        self.LinePlotModel.run_model(r_script)

class BoxPlotController:
    """_summary_box_plot_controller_
    This class is responsible for controlling the BoxPlotModel.
    Attributes:
        BoxPlotModel (BoxPlotModel): An instance of the BoxPlotModel class.
    Methods:
        __init__(BoxPlotModel):
            Initializes the BoxPlotController with a BoxPlotModel instance.
        run_model(r_script):
            Executes the run_model method of the BoxPlotModel with the provided
            R script.
    """
    def __init__(self, BoxPlotModel):
        self.BoxPlotModel = BoxPlotModel
    
    def run_model(self, r_script):
        self.BoxPlotModel.run_model(r_script)

class HistogramController:
    """_summary_histogram_controller_
    This class is responsible for controlling the HistogramModel.
    Attributes:
        HistogramModel (HistogramModel): An instance of the HistogramModel class.
    Methods:
        __init__(HistogramModel):
            Initializes the HistogramController with a HistogramModel instance.
        run_model(r_script):
            Executes the run_model method of the HistogramModel with the provided
            R script.
    """
    def __init__(self, HistogramModel):
        self.HistogramModel = HistogramModel
    
    def run_model(self, r_script):
        self.HistogramModel.run_model(r_script)