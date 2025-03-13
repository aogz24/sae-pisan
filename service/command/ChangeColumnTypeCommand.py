from PyQt6.QtGui import QUndoCommand
import polars as pl

class ChangeColumnTypeCommand(QUndoCommand):
    """
    A command class to change the data type of a column in a model, supporting undo and redo operations.
    Attributes:
        model (QAbstractTableModel): The model containing the data.
        column_index (int): The index of the column to change.
        old_dtype (str): The original data type of the column.
        new_dtype (str): The new data type of the column.
        old_data (list): The original data of the column.
        new_data (list): The new data of the column.
        column_name (str): The name of the column to change.
    Methods:
        undo(): Reverts the column to its original data type and data.
        redo(): Changes the column to the new data type and data.
    """
    
    def __init__(self, model, column_index, old_dtype, new_dtype, old_data, new_data):
        super().__init__()
        self.model = model
        self.column_index = column_index
        self.old_dtype = old_dtype
        self.new_dtype = new_dtype
        self.old_data = old_data
        self.new_data = new_data
        self.column_name = self.model._data.columns[self.column_index]
        self.setText(f"Change column type of {self.column_name} from {self.old_dtype} to {self.new_dtype}")

    def undo(self):
        self.model.beginResetModel()
        self.model._data = self.model._data.with_columns([pl.Series(self.column_name, self.old_data).cast(self.old_dtype)])
        self.model.endResetModel()

    def redo(self):
        self.model.beginResetModel()
        self.model._data = self.model._data.with_columns([pl.Series(self.column_name, self.new_data).cast(self.new_dtype)])
        self.model.endResetModel()