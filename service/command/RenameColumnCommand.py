from PyQt6.QtGui import QUndoCommand

class RenameColumnCommand(QUndoCommand):
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