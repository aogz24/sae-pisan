from model.SaeModelling import SaeModelling
from service.modelling.running_model.SaeEblupArea import RunModelEblupArea

class SaeEblup(SaeModelling):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def RunModel(self, r_script):
        self.r_script = r_script
        RunModelEblupArea(self)
    
    def get_model2(self):
        return self.model2