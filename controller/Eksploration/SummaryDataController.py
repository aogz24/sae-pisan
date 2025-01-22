class SummaryDataController:
    def __init__(self, SummaryData):
        self.SummaryData = SummaryData
    
    def run_model(self, r_script):
        self.SummaryData.run_model(r_script)