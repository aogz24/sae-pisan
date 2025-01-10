from PyQt6.QtWidgets import QTableWidgetItem
from PyQt6.QtCore import Qt
import polars as pl
from PyQt6 import QtCore, QtGui, QtWidgets
from service.command.EditDataCommand import EditDataCommand
from service.command.AddRowCommand import AddRowsCommand
from service.command.AddColumnCommand import AddColumnCommand
from service.command.DeleteRowCommand import DeleteRowCommand
from PyQt6.QtGui import QKeySequence, QUndoStack

class TableModel(QtCore.QAbstractTableModel):
    def __init__(self, data, batch_size=100):
        super().__init__()
        self._data = data
        self.undo_stack = QUndoStack()
        self.batch_size = batch_size
        self.loaded_rows = min(batch_size, self._data.shape[0])

    def data(self, index, role):
        if role == Qt.ItemDataRole.DisplayRole or role == Qt.ItemDataRole.EditRole:
            value = self._data[index.row(), index.column()]
            return str(value)

    def rowCount(self, index):
        return self.loaded_rows

    def columnCount(self, index):
        return self._data.shape[1]

    def headerData(self, section, orientation, role):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                if section < len(self._data.columns):
                    return str(self._data.columns[section])
                return ""
            if orientation == Qt.Orientation.Vertical:
                return str(section + 1)

    def flags(self, index):
        return (
            Qt.ItemFlag.ItemIsSelectable
            | Qt.ItemFlag.ItemIsEnabled
            | Qt.ItemFlag.ItemIsEditable
        )

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        if role == Qt.ItemDataRole.EditRole:
            row = index.row()
            column = index.column()

            column_name = self._data.columns[column]
            dtype = self._data[column_name].dtype

            old_value = self._data[row, column]

            if dtype == pl.Float64:
                try:
                    if isinstance(value, str):
                        if value.count(',') == 1 and value.replace(',', '').isdigit():
                            value = value.replace(',', '.')
                        value = float(value)
                except ValueError:
                    error_dialog = QtWidgets.QMessageBox()
                    error_dialog.setIcon(QtWidgets.QMessageBox.Icon.Warning)
                    error_dialog.setText(f"Invalid value: {value} for column {column_name}. Expected a numeric value.")
                    error_dialog.setInformativeText("Do you want to set the column as a string?")
                    error_dialog.setWindowTitle("Invalid Input")
                    error_dialog.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No)
                    error_dialog.setDefaultButton(QtWidgets.QMessageBox.StandardButton.No)
                    ret = error_dialog.exec()

                    if ret == QtWidgets.QMessageBox.StandardButton.Yes:
                        dtype = pl.Utf8
                        self._data = self._data.with_columns([pl.col(column_name).cast(dtype)])
                    else:
                        return False

            if dtype == pl.Int64:
                try:
                    if isinstance(value, str):
                        value = int(value)
                except ValueError:
                    error_dialog = QtWidgets.QMessageBox()
                    error_dialog.setIcon(QtWidgets.QMessageBox.Icon.Warning)
                    error_dialog.setText(f"Invalid value: {value} for column {column_name}. Expected an integer value.")
                    error_dialog.setInformativeText("Do you want to set column to a string?")
                    error_dialog.setWindowTitle("Invalid Input")
                    error_dialog.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No)
                    error_dialog.setDefaultButton(QtWidgets.QMessageBox.StandardButton.No)
                    ret = error_dialog.exec()

                    if ret == QtWidgets.QMessageBox.StandardButton.Yes:
                        dtype = pl.Utf8
                        self._data = self._data.with_columns([pl.col(column_name).cast(dtype)])
                    else:
                        return False

            self._data[row, column] = value
            self.dataChanged.emit(index, index)
            command = EditDataCommand(self, row, column, old_value, value)  # Pass row, column to command
            self.undo_stack.push(command)
            return True
        return False


    def set_data(self, new_data):
        if isinstance(new_data, pl.DataFrame):
            self.beginResetModel()
            self._data = new_data
            self.loaded_rows = min(self.batch_size, self._data.shape[0])
            self.endResetModel()
        else:
            raise ValueError("Data must be a Polars DataFrame")
    
    def get_data(self):
        return self._data

    def copy(self, index):
        if index.isValid():
            value = self.data(index, Qt.ItemDataRole.DisplayRole)
            clipboard = QtGui.QGuiApplication.clipboard()
            clipboard.setText(value)

    def paste(self, index):
        if index.isValid():
            clipboard = QtGui.QGuiApplication.clipboard()
            value = clipboard.text()
            self.setData(index, value)

    def undo(self):
        self.undo_stack.undo()

    def redo(self):
        self.undo_stack.redo()

    def canFetchMore(self, index):
        return self.loaded_rows < self._data.shape[0]

    def fetchMore(self, index):
        remaining_rows = self._data.shape[0] - self.loaded_rows
        rows_to_fetch = min(self.batch_size, remaining_rows)
        self.beginInsertRows(QtCore.QModelIndex(), self.loaded_rows, self.loaded_rows + rows_to_fetch - 1)
        self.loaded_rows += rows_to_fetch
        self.endInsertRows()
    
    def addRowsBefore(self, index, count):
        if index.isValid() and count > 0:
            print("Adding rows before")
            row = index.row()
            new_rows = [{col: None if self._data[col].dtype in [pl.Int64, pl.Float64] else "" for col in self._data.columns} for _ in range(count)]
            self.beginInsertRows(QtCore.QModelIndex(), row, row + count - 1)
            self._data = pl.concat([self._data[:row], pl.DataFrame(new_rows), self._data[row:]])
            self.loaded_rows += count
            self.endInsertRows()
            command = AddRowsCommand(self, row, new_rows)
            self.undo_stack.push(command)

    def addRowsAfter(self, index, count):
        if index.isValid() and count > 0:
            row = index.row() + 1
            new_rows = [{col: None if self._data[col].dtype in [pl.Int64, pl.Float64] else "" for col in self._data.columns} for _ in range(count)]
            self.beginInsertRows(QtCore.QModelIndex(), row, row + count - 1)
            self._data = pl.concat([self._data[:row], pl.DataFrame(new_rows), self._data[row:]])
            self.loaded_rows += count
            self.endInsertRows()
            command = AddRowsCommand(self, row, new_rows)
            self.undo_stack.push(command)
    
    def addColumnBefore(self, index, count):
        if index.isValid() and count > 0:
            column = index.column()
            new_columns = {f"new_col_{i}": [""] * self._data.shape[0] for i in range(count)}
            self.beginResetModel()
            self._data = pl.concat([self._data[:, :column], pl.DataFrame(new_columns), self._data[:, column:]], how="horizontal")
            self.endResetModel()
            column_names = list(new_columns.keys())  # Extract column names
            new_columns_data = list(new_columns.values())  # Extract column data
            command = AddColumnCommand(self, column_names, new_columns_data)
            self.undo_stack.push(command)

    def addColumnAfter(self, index, count):
        if index.isValid() and count > 0:
            column = index.column() + 1
            new_columns = {f"new_col_{i}": [""] * self._data.shape[0] for i in range(count)}
            self.beginResetModel()
            self._data = pl.concat([self._data[:, :column], pl.DataFrame(new_columns), self._data[:, column:]], how="horizontal")
            self.endResetModel()
            column_names = list(new_columns.keys())
            new_columns_data = list(new_columns.values())
            command = AddColumnCommand(self, column_names, new_columns_data)
            self.undo_stack.push(command)
    
    def deleteRow(self, index):
        if index.isValid():
            row = index.row()
            old_row = self._data[row].to_dict(as_series=False)
            self.beginRemoveRows(QtCore.QModelIndex(), row, row)
            self._data = pl.concat([self._data[:row], self._data[row + 1:]])
            self.loaded_rows -= 1
            self.endRemoveRows()
            command = DeleteRowCommand(self, row, old_row)
            self.undo_stack.push(command)

    def deleteColumn(self, index):
        if index.isValid():
            column = index.column()
            column_name = self._data.columns[column]
            old_column = self._data[column_name].to_list()
            self.beginResetModel()
            self._data = self._data.drop(column_name)
            self.endResetModel()
            command = DeleteColumnCommand(self, column, column_name, old_column)
            self.undo_stack.push(command)
    