class NormalityTestController:
    def __init__(self,NormalityTestModel):
        self.NormalityTestModel = NormalityTestModel

    def run_model(self, r_script):
        self.NormalityTestModel.run_model(r_script)