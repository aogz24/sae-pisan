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
        self.Normal = True
        
        # Reset dialog state to ensure clean initialization
        self._reset_dialog_state()
        
        # Show vardir components for Normal model
        self.assign_vardir_button.setEnabled(True)
        self.assign_vardir_button.setVisible(True)
        self.vardir_label.setVisible(True)
        self.vardir_list.setVisible(True)
    
    def _reset_dialog_state(self):
        """Reset the dialog to its initial state"""
        # Clear all assignments
        self.of_interest_var = []
        self.auxilary_vars = []
        self.vardir_var = []
        self.as_factor_var = []
        
        # Reset models
        self.of_interest_model.setStringList([])
        self.auxilary_model.setStringList([])
        self.as_factor_model.setStringList([])
        self.vardir_model.setStringList([])
        
        # Reset options to default
        self.selection_method = "None"
        self.iter_update = "3"
        self.iter_mcmc = "2000"
        self.burn_in = "1000"
        
        # Clear script area
        self.r_script_edit.clear()