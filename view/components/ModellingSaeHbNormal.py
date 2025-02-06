from view.components.ModellingSaeHBDialog import ModelingSaeHBDialog

class ModelingSaeHBNormalDialog(ModelingSaeHBDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("SAE HB Normal")
        self.model_method = "Normal"