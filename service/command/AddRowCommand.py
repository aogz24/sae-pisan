from PyQt6.QtGui import QUndoCommand
import polars as pl
from PyQt6 import QtCore

class AddRowsCommand(QUndoCommand):
    """
    A command class to add rows to a model, supporting undo and redo operations.
    Attributes:
        model (QAbstractItemModel): The model to which rows will be added.
        row (int): The position at which new rows will be inserted.
        new_rows (list): The new rows to be added to the model.
        executed (bool): A flag to prevent re-execution during the initial push.
    Methods:
        undo():
            Removes the previously added rows from the model.
        redo():
            Adds the new rows to the model. If the command has already been executed,
            it will insert the rows again.
    """
    
    def __init__(self, model, row, new_rows):
        super().__init__()
        self.model = model
        self.row = row
        self.new_rows = new_rows
        self.executed = False

    def undo(self):
        self.model.beginRemoveRows(QtCore.QModelIndex(), self.row, self.row + len(self.new_rows) - 1)
        self.model._data = pl.concat([self.model._data[:self.row], self.model._data[self.row + len(self.new_rows):]])
        self.model.loaded_rows -= len(self.new_rows)
        self.model.endRemoveRows()

    def redo(self):
        if not self.executed:  # Cegah eksekusi ulang saat push
            self.executed = True
        else:
            self.model.beginInsertRows(QtCore.QModelIndex(), self.row, self.row + len(self.new_rows) - 1)
            self.model._data = pl.concat([self.model._data[:self.row], pl.DataFrame(self.new_rows), self.model._data[self.row:]])
            self.model.loaded_rows += len(self.new_rows)
            self.model.endInsertRows()