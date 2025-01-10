from PyQt6.QtGui import QUndoCommand
import polars as pl
from PyQt6 import QtCore

class AddColumnCommand(QUndoCommand):
    def __init__(self, model, column_names, new_columns):
        """
        Initializes the AddColumnCommand with model, column names, and the corresponding new columns.

        :param model: The model containing the data.
        :param column_names: A list of column names to be added.
        :param new_columns: A list of lists with the new column data (one list per column).
        """
        super().__init__()
        self.model = model
        self.column_names = column_names
        self.new_columns = new_columns
        self.executed = False

    def undo(self):
        """
        Undo the addition of columns by removing them from the DataFrame.
        """
        for column_name in self.column_names:
            if column_name in self.model._data.columns:
                col_index = self.model._data.columns.index(column_name)
                self.model.beginRemoveColumns(QtCore.QModelIndex(), col_index, 1)
                self.model._data = self.model._data.drop(column_name)
                self.model.endRemoveColumns()

    def redo(self):
        """
        Redo the addition of columns by inserting them into the DataFrame.
        """
        if not self.executed:
            self.executed = True
        else:
            for column_name, new_column in zip(self.column_names, self.new_columns):
                self.model.beginInsertColumns(QtCore.QModelIndex(), self.model._data.width, self.model._data.width)
                self.model._data = self.model._data.with_columns(pl.Series(column_name, new_column))
                self.model.endInsertColumns()
