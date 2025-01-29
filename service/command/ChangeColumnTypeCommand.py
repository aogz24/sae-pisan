from PyQt6.QtGui import QUndoCommand
import polars as pl

class ChangeColumnTypeCommand(QUndoCommand):
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