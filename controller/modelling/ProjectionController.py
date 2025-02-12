class ProjectionController:
    def __init__(self, projectionModel):
        self.projectionModel = projectionModel
    
    def run_model(self, r_script):
        self.projectionModel.run_model(r_script)