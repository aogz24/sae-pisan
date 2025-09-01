from PyQt6.QtGui import QUndoCommand
import polars as pl

class LoadDataCommand(QUndoCommand):
    """
    Command class for loading data to the main model.
    This command will save the old state of the model before loading new data,
    allowing for undo and redo operations.
    """
    
    def __init__(self, model, new_data):
        """
        Initializes the LoadDataCommand with model and new data.

        :param model: The model containing the data.
        :param new_data: The new data to be loaded into the model.
        """
        super().__init__()
        self.model = model
        self.new_data = new_data
        self.old_data = model.get_data()
        self.setText("Load Data")

    def undo(self):
        """
        Undo the loading of data by restoring the previous data.
        """
        self.model.set_data(self.old_data)

    def redo(self):
        """
        Redo the loading of data by setting the new data again.
        """
        self.model.set_data(self.new_data)
