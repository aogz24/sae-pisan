from view.components.ModellingSaeHBDialog import ModelingSaeHBDialog

class ModelingSaeHBNormalDialog(ModelingSaeHBDialog):
    """
    A dialog class for modeling SAE HB with a normal distribution.
    Inherits from:
        ModelingSaeHBDialog: The base class for SAE HB modeling dialogs.
    Attributes:
        model_method (str): The method used for modeling, set to "Normal".
    Methods:
        __init__(parent): Initializes the dialog with the given parent.
    """
    
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("SAE HB Normal")
        self.model_method = "Normal"