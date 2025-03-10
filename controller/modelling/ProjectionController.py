class ProjectionController:
    def __init__(self, projectionModel):
        self.projectionModel = projectionModel
    
    def run_model(self, r_script):
        result, error, df = self.SAEmodel.run_model(r_script)
        return result, error, df