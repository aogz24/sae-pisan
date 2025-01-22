from model.SaeModelling import SaeModelling
from service.modelling.running_model.SaeHBArea import run_model_hb_area

class SaeHB(SaeModelling):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.result = ""
        
    def run_model(self, r_script):
        self.r_script = r_script
        run_model_hb_area(self)
    
    def get_model2(self):
        return self.model2