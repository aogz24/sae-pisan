from PyQt6.QtCore import QModelIndex
from PyQt6.QtGui import QUndoCommand
import polars as pl

class DeleteRowCommand(QUndoCommand):
    def __init__(self, model, row, old_row):
        super().__init__()
        self.model = model
        self.row = row
        self.old_row = old_row
        self.executed = False

    def undo(self):
        self.model.beginInsertRows(QModelIndex(), self.row, self.row)
        self.model._data = pl.concat([self.model._data[:self.row], pl.DataFrame(self.old_row), self.model._data[self.row:]])
        self.model.loaded_rows += 1
        self.model.endInsertRows()

    def redo(self):
        if not self.executed:  # Cegah eksekusi ulang saat push
            self.executed = True
        else:
            self.model.beginRemoveRows(QModelIndex(), self.row, self.row)
            self.model._data = pl.concat([self.model._data[:self.row], self.model._data[self.row + 1:]])
            self.model.loaded_rows -= 1
            self.model.endRemoveRows()