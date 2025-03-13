from PyQt6.QtCore import Qt
import polars as pl
from PyQt6 import QtCore, QtGui, QtWidgets
from service.command.EditDataCommand import EditDataCommand
from service.command.AddRowCommand import AddRowsCommand
from service.command.AddColumnCommand import AddColumnCommand
from service.command.DeleteRowsCommand import DeleteRowsCommand
from service.command.DeleteColumnsCommand import DeleteColumnsCommand
from PyQt6.QtGui import QUndoStack
from service.command.ChangeColumnTypeCommand import ChangeColumnTypeCommand
from service.command.RenameColumnCommand import RenameColumnCommand

class TableModel(QtCore.QAbstractTableModel):
    """A custom table model for handling data in a Qt application with support for undo/redo operations.
    Attributes:
        _data (pl.DataFrame): The data to be displayed in the table.
        undo_stack (QUndoStack): Stack to manage undo/redo operations.
        batch_size (int): Number of rows to load initially.
        loaded_rows (int): Number of rows currently loaded.
    Methods:
        __init__(data, batch_size=100):
            Initializes the table model with data and batch size.
        data(index, role):
            Returns the data for the given index and role.
        rowCount(_):
            Returns the number of rows in the table.
        columnCount(_):
            Returns the number of columns in the table.
        headerData(section, orientation, role):
            Returns the header data for the given section, orientation, and role.
        flags(_):
            Returns the item flags for the table.
        setData(index, value, role=Qt.ItemDataRole.EditRole):
            Sets the data for the given index and role.
        set_data(new_data):
            Sets the entire data for the table.
        get_data():
            Returns the current data of the table.
        copy(index):
            Copies the data at the given index to the clipboard.
        paste(index):
            Pastes the data from the clipboard to the given index.
        undo():
            Undoes the last operation.
        redo():
            Redoes the last undone operation.
        canFetchMore(_):
            Checks if more rows can be fetched.
        fetchMore(_):
            Fetches more rows to be displayed in the table.
        addRowsBefore(index, count):
            Adds rows before the given index.
        addRowsAfter(index, count):
            Adds rows after the given index.
        addColumnBefore(index, count):
            Adds columns before the given index.
        addColumnAfter(index, count):
            Adds columns after the given index.
        deleteRows(start_row, count):
            Deletes rows starting from the given row index.
        deleteColumns(start_column, count):
            Deletes columns starting from the given column index.
        rename_column(column_index, new_name):
            Renames the column at the given index to the new name.
        get_column_type(column_index):
            Returns the data type of the column at the given index.
        set_column_type(column_index, new_type):
            Sets the data type of the column at the given index to the new type."""
    
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

    def rowCount(self, _):
        return self.loaded_rows

    def columnCount(self, _):
        return self._data.shape[1]

    def headerData(self, section, orientation, role):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                if section < len(self._data.columns):
                    column_name = self._data.columns[section]
                    return f"{column_name}"
                return ""
            if orientation == Qt.Orientation.Vertical:
                return str(section + 1)
        elif role == Qt.ItemDataRole.DecorationRole or role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                if section < len(self._data.columns):
                    column_name = self._data.columns[section]
                    dtype = self._data[column_name].dtype
                    if dtype == pl.Utf8:
                        return QtGui.QIcon("assets/nominal.svg")
                    else:
                        return QtGui.QIcon("assets/numeric.svg")
        return None

    def flags(self, _):
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

    def canFetchMore(self, _):
        return self.loaded_rows < self._data.shape[0]

    def fetchMore(self, _):
        if self.loaded_rows >= self._data.shape[0]:
            return
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
    
    def deleteRows(self, start_row, count):
        if start_row >= 0 and count > 0:
            old_rows = self._data[start_row:start_row + count].to_dict(as_series=False)
            self.beginRemoveRows(QtCore.QModelIndex(), start_row, start_row + count - 1)
            self._data = pl.concat([self._data[:start_row], self._data[start_row + count:]])
            self.loaded_rows -= count
            self.endRemoveRows()
            command = DeleteRowsCommand(self, start_row, old_rows)
            self.undo_stack.push(command)

    def deleteColumns(self, start_column, count):
        """
        Deletes columns starting from `start_column` and spanning `count` columns.

        Args:
            start_column (int): The starting column index to delete.
            count (int): The number of columns to delete.
        """
        if start_column >= 0 and count > 0:
            # Store original column order
            original_order = self._data.columns

            # Store the deleted columns and their data
            old_columns = {
                self._data.columns[i]: self._data[:, i].to_list()
                for i in range(start_column, start_column + count)
            }
            self.beginResetModel()
            columns_to_keep = [
                col for i, col in enumerate(self._data.columns)
                if i < start_column or i >= start_column + count
            ]
            self._data = self._data.select(columns_to_keep)
            self.endResetModel()

            # Create a DeleteColumnsCommand and push it to the undo stack
            command = DeleteColumnsCommand(self, start_column, old_columns, original_order)
            self.undo_stack.push(command)

    
    def rename_column(self, column_index, new_name):
        if isinstance(column_index, int) and 0 <= column_index < len(self._data.columns):
            old_name = self._data.columns[column_index]
            self.beginResetModel()
            self._data = self._data.rename({old_name: new_name})
            self.endResetModel()
            command = RenameColumnCommand(self, column_index, old_name, new_name)
            self.undo_stack.push(command)
    
    def get_column_type(self, column_index):
        if isinstance(column_index, int) and 0 <= column_index < len(self._data.columns):
            column_name = self._data.columns[column_index]
            return self._data[column_name].dtype
        return None

    def set_column_type(self, column_index, new_type):
        if isinstance(column_index, int) and 0 <= column_index < len(self._data.columns):
            column_name = self._data.columns[column_index]
            old_dtype = self._data[column_name].dtype
            old_data = self._data[column_name].to_list()

            if new_type == "String":
                new_dtype = pl.Utf8
            elif new_type == "Integer":
                if self._data[column_name].dtype == pl.Utf8:
                    try:
                        warning_dialog = QtWidgets.QMessageBox()
                        warning_dialog.setIcon(QtWidgets.QMessageBox.Icon.Warning)
                        warning_dialog.setText(f"The current data type of column {column_name} is String. Converting to Integer will result in loss of non-numeric data.")
                        warning_dialog.setInformativeText("Do you want to proceed with the conversion?")
                        warning_dialog.setWindowTitle("Data Type Conversion Warning")
                        warning_dialog.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No)
                        warning_dialog.setDefaultButton(QtWidgets.QMessageBox.StandardButton.No)
                        ret = warning_dialog.exec()

                        if ret == QtWidgets.QMessageBox.StandardButton.Yes:
                            self._data = self._data.with_columns([
                                pl.when(pl.col(column_name).str.contains(r'\d'))
                                .then(pl.col(column_name).str.extract(r'(\d+)').cast(pl.Int64))
                                .otherwise(pl.lit(None).cast(pl.Int64))
                            ])
                        else:
                            return
                    except Exception:
                        raise ValueError(f"Cannot convert column {column_name} to Integer")
                new_dtype = pl.Int64
            elif new_type == "Float":
                if self._data[column_name].dtype == pl.Utf8:
                    try:
                        warning_dialog = QtWidgets.QMessageBox()
                        warning_dialog.setIcon(QtWidgets.QMessageBox.Icon.Warning)
                        warning_dialog.setText(f"The current data type of column {column_name} is String. Converting to Float will result in loss of non-numeric data.")
                        warning_dialog.setInformativeText("Do you want to proceed with the conversion?")
                        warning_dialog.setWindowTitle("Data Type Conversion Warning")
                        warning_dialog.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No)
                        warning_dialog.setDefaultButton(QtWidgets.QMessageBox.StandardButton.No)
                        ret = warning_dialog.exec()

                        if ret == QtWidgets.QMessageBox.StandardButton.Yes:
                            self._data = self._data.with_columns([
                                pl.when(pl.col(column_name).str.contains(r'^\d+(\.\d+)?$') | pl.col(column_name).str.contains(r'^\d+(,\d+)?$'))
                                .then(pl.col(column_name).str.replace(",", ".").cast(pl.Float64, strict=False))
                                .otherwise(pl.lit(None).cast(pl.Float64))
                            ])
                        else:
                            return
                    except Exception:
                        raise ValueError(f"Cannot convert column {column_name} to Float")
                new_dtype = pl.Float64
            else:
                raise ValueError("Unsupported data type")

            self.beginResetModel()
            self._data = self._data.with_columns([pl.col(column_name).cast(new_dtype)])
            self.endResetModel()

            command = ChangeColumnTypeCommand(self, column_index, old_dtype, new_dtype, old_data, self._data[column_name].to_list())
            self.undo_stack.push(command)
            
