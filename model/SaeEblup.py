from model.SaeModelling import SaeModelling
from service.modelling.running_model.SaeEblupArea import run_model_eblup_area

class SaeEblup(SaeModelling):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.result ="cekek"
    
    def run_model(self, r_script):
        self.r_script = r_script
        result, error, df = run_model_eblup_area(self)
        return result, error, df
    
    def get_model2(self):
        return self.model2