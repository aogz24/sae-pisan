from PyQt6.QtGui import QUndoCommand

class RenameColumnCommand(QUndoCommand):
    """
    A command to rename a column in a model, supporting undo and redo operations.
    Attributes:
        model (QAbstractItemModel): The model containing the data.
        column_index (int): The index of the column to rename.
        old_name (str): The current name of the column.
        new_name (str): The new name for the column.
        executed (bool): Flag indicating whether the command has been executed.
    Methods:
        redo(): Renames the column to the new name.
        undo(): Reverts the column name to the old name.
    """
    """
    Initializes the RenameColumnCommand with the model, column index, old name, and new name.
    Args:
        model (QAbstractItemModel): The model containing the data.
        column_index (int): The index of the column to rename.
        old_name (str): The current name of the column.
        new_name (str): The new name for the column.
    """
    """
    Renames the column to the new name. If the command has already been executed,
    it updates the model's data and emits the layoutChanged signal.
    """
    """
    Reverts the column name to the old name. If the command has already been executed,
    it updates the model's data and emits the layoutChanged signal.
    """
    
    def __init__(self, model, column_index, old_name, new_name):
        super().__init__()
        self._model = model
        self._column_index = column_index
        self._old_name = old_name
        self._new_name = new_name
        self.executed = False

    def redo(self):
        if not self.executed:
            self.executed = True
        else:
            self._model._data = self._model._data.rename({self._old_name: self._new_name})
            self._model.layoutChanged.emit()

    def undo(self):
        if not self.executed:
            self.executed = True
        else:
            self._model._data = self._model._data.rename({self._new_name: self._old_name})
            self._model.layoutChanged.emit()