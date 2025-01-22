from SaeModelling import SaeModelling

class SaeHB(SaeModelling):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def run_model(self, r_script):
        self.r_script = r_script
        # run_model_eblup_area(self)
    
    def get_model2(self):
        return self.model2