from PyQt6.QtCore import QThread, pyqtSignal

class RunModelThread(QThread):
    finished = pyqtSignal(object, object, object)  # Signal to emit when the model run is finished

    def __init__(self, controller, r_script, parent):
        super().__init__()
        self.controller = controller
        self.r_script = r_script
        self.parent = parent

    def run(self):
        self.controller.run_model(self.r_script)
        sae_model = self.controller.model
        self.finished.emit(self.parent, self.r_script, sae_model)