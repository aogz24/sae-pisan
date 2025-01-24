from PyQt6.QtCore import QModelIndex
from PyQt6.QtGui import QUndoCommand
import polars as pl

class DeleteRowsCommand(QUndoCommand):
    def __init__(self, model, start_row, rows_data):
        super().__init__("Delete Rows")
        self.model = model
        self.start_row = start_row
        self.rows_data = pl.DataFrame(rows_data) if not isinstance(rows_data, pl.DataFrame) else rows_data
        self.executed = False

    def undo(self):
        self.model.beginInsertRows(QModelIndex(), self.start_row, self.start_row + len(self.rows_data) - 1)
        self.model._data = pl.concat([pl.DataFrame(self.model._data[:self.start_row]), self.rows_data, pl.DataFrame(self.model._data[self.start_row:])])
        self.model.loaded_rows = min(self.model.loaded_rows + len(self.rows_data), self.model._data.shape[0])
        self.model.endInsertRows()
        self.model.layoutChanged.emit()

    def redo(self):
        if not self.executed:  # Prevent re-execution when pushed
            self.executed = True
        else:
            self.model.beginRemoveRows(QModelIndex(), self.start_row, self.start_row + len(self.rows_data) - 1)
            self.model._data = pl.concat([self.model._data[:self.start_row], self.model._data[self.start_row + len(self.rows_data):]])
            self.model.loaded_rows = max(self.model.loaded_rows - len(self.rows_data), 0)
            self.model.endRemoveRows()
            self.model.layoutChanged.emit()
