from PyQt6.QtGui import QUndoCommand
import polars as pl

class DeleteColumnsCommand(QUndoCommand):
    def __init__(self, model, start_column, deleted_columns, original_order):
        """
        Initialize the DeleteColumnsCommand.

        Args:
            model: The model to apply the changes to.
            start_column: The index of the first column to delete.
            deleted_columns: A dictionary of deleted column names and their data.
            original_order: The original order of columns before deletion.
        """
        super().__init__()
        self.model = model
        self.start_column = start_column
        self.deleted_columns = deleted_columns
        self.old_data = deleted_columns  # Store the columns that were deleted
        self.original_order = original_order  # Store the original column order
        self.executed = False

    def undo(self):
        """Undo the column deletion by restoring the deleted columns."""
        self.model.beginResetModel()
        for col_name, col_values in self.deleted_columns.items():
            self.model._data = self.model._data.with_columns(pl.Series(col_name, col_values))

        # Reorder columns to match the original order
        self.model._data = self.model._data.select(self.original_order)
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