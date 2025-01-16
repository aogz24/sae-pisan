from PyQt6.QtGui import QUndoCommand

class EditDataCommand(QUndoCommand):
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