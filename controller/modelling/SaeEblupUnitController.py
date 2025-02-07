class SaeEblupUnitController:
    def __init__(self, SAEmodel):
        self.SAEmodel = SAEmodel
    
    def run_model(self, r_script):
        self.SAEmodel.run_model(r_script)