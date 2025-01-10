from PyQt6.QtGui import QUndoCommand
import polars as pl

class DeleteColumnsCommand(QUndoCommand):
    def __init__(self, model, start_column, deleted_columns):
        super().__init__()
        self.model = model
        self.start_column = start_column
        self.deleted_columns = deleted_columns
        self.old_data = deleted_columns  # Store the columns that were deleted
        self.executed = False

    def undo(self):
        """Undo the column deletion by restoring the deleted columns."""
        self.model.beginResetModel()
        for col_name, col_values in self.deleted_columns.items():
            self.model._data = self.model._data.with_columns(pl.Series(col_name, col_values))
        self.model.endResetModel()

    def redo(self):
        """Redo the column deletion by removing the columns again."""
        if not self.executed:
            self.executed = True
        else:
            self.model.beginResetModel()
            columns_to_remove = list(self.deleted_columns.keys())
            self.model._data = self.model._data.select(
                [col for col in self.model._data.columns if col not in columns_to_remove]
            )
            self.model.endResetModel()
