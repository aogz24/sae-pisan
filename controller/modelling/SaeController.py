class SaeController:
    def __init__(self, SAEmodel, model2):
        self.SAEmodel = SAEmodel
        self.model2 = model2
    
    def run_model(self, r_script):
        self.SAEmodel.run_model(r_script)