from service.exploration.BoxPlot import run_box_plot

class BoxPlot:
    def __init__(self, model1, model2, view):
        self.model1 = model1
        self.model2 = model2
        self.view = view
        self.plot = None

    def run_model(self, r_script):
        self.r_script = r_script
        run_box_plot(self)

    def activate_R(self):
        from rpy2.robjects import pandas2ri
        pandas2ri.activate()
    
