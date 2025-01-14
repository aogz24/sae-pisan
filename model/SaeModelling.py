class SaeModelling:
    def __init__(self, model1, model2, view):
        self.model1 = model1
        self.model2 = model2
        self.view = view
        
    def activate_R(self):
        from rpy2.robjects import pandas2ri
        pandas2ri.activate()