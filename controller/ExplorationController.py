from PyQt6.QtWidgets import QMessageBox, QDialog
from view.components.SummaryDialog import SummaryDialog  # Dialog for selecting columns


class ExplorationController:
    def __init__(self, model1, model2, view):
        self.model1 = model1
        self.model2 = model2
        self.view = view

        # Connect the action "Summary Data" to the function in the controller
        self.view.action_summary_data.triggered.connect(self.on_summary_clicked)

    def on_summary_clicked(self):
        """Handler for the action 'Summary Data'"""
        print("Summary Data clicked")
        dialog = SummaryDialog(self.model1,self.model2)
        dialog.exec() 
