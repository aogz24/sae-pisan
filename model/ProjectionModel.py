from model.SaeModelling import SaeModelling
from service.modelling.running_model.Projection import run_model_projection

class Projection(SaeModelling):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.result = ""
    
    def run_model(self, r_script):
        self.r_script = r_script
        run_model_projection(self)
    
    def get_model2(self):
        return self.model2