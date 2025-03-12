from model.SaeModelling import SaeModelling
from service.modelling.running_model.SaeEblupPseudo import run_model_eblup_pseudo

class SaeEblupPseudo(SaeModelling):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def run_model(self, r_script):
        self.r_script = r_script
        result, error, df = run_model_eblup_pseudo(self)
        return result, error, df
    
    def get_model2(self):
        return self.model2