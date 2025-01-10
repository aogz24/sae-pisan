from PyQt6.QtGui import QUndoCommand
import polars as pl
from PyQt6 import QtCore

class DeleteColumnCommand(QUndoCommand):
    def __init__(self, model, column, column_name, old_column):
        """
        Initializes the DeleteColumnCommand with model, column, column name, and old column.

        :param model: The model containing the data.
        :param column: The column to be deleted.
        :param column_name: The name of the column to be deleted.
        :param old_column: The old column data.
        """
        super().__init__()
        self.model = model
        self.column = column
        self.column_name = column_name
        self.old_column = old_column
        self.deleted_columns = {}
        self.executed = False

    def undo(self):
        """
        Undo the deletion of columns by re-adding them to the DataFrame.
        """
        for column_name, column_data in self.deleted_columns.items():
            self.model.beginInsertColumns(QtCore.QModelIndex(), self.model._data.width, self.model._data.width)
            self.model._data = self.model._data.with_columns(pl.Series(column_name, column_data))
            self.model.endInsertColumns()

    def redo(self):
        """
        Redo the deletion of columns by removing them from the DataFrame.
        """
        if not self.executed:
            self.executed = True
        else: 
            for column_name in self.column_names:
                if column_name in self.model._data.columns:
                    self.deleted_columns[column_name] = self.model._data[column_name]
                    col_index = self.model._data.columns.index(column_name)
                    self.model.beginRemoveColumns(QtCore.QModelIndex(), col_index, 1)
                    self.model._data = self.model._data.drop(column_name)
                    self.model.endRemoveColumns()