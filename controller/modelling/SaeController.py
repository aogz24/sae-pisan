class SaeController:
    def __init__(self, SAEmodel, model2):
        self.SAEmodel = SAEmodel
        self.model2 = model2
    
    def RunModel(self, r_script):
        self.SAEmodel.RunModel(r_script)