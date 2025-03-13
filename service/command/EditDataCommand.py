from PyQt6.QtGui import QUndoCommand

class EditDataCommand(QUndoCommand):
    """
    Command to edit data in a cell.
    This command is used to change the value of a specific cell in a model.
    It supports undo and redo operations to revert or reapply the changes.
    Attributes:
        model: The model containing the data to be edited.
        row: The row index of the cell to be edited.
        column: The column index of the cell to be edited.
        old_value: The original value of the cell before the edit.
        new_value: The new value to be set in the cell.
    Methods:
        undo(): Reverts the cell value to the original value.
        redo(): Applies the new value to the cell.
    """
    
    """Command untuk mengubah data dalam sel"""
    def __init__(self, model, row, column, old_value, new_value):
        super().__init__()
        self.model = model  # Model passed as argument
        self.row = row
        self.column = column
        self.old_value = old_value
        self.new_value = new_value
        self.setText(f"Edit cell at ({row}, {column})")  # Deskripsi untuk command

    def undo(self):
        """Kembalikan ke nilai sebelumnya"""
        # Update model data
        self.model._data[self.row, self.column] = self.old_value
        self.model.dataChanged.emit(self.model.createIndex(self.row, self.column), self.model.createIndex(self.row, self.column))

    def redo(self):
        """Terapkan perubahan baru"""
        # Update model data
        self.model._data[self.row, self.column] = self.new_value
        self.model.dataChanged.emit(self.model.createIndex(self.row, self.column), self.model.createIndex(self.row, self.column))