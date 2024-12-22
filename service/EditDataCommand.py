from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QApplication
from PyQt6.QtGui import QKeySequence, QUndoStack, QUndoCommand
from PyQt6.QtCore import Qt
import pandas as pd

class EditDataCommand(QUndoCommand):
    """Command untuk mengubah data dalam sel"""
    def __init__(self, table_widget, row, column, old_value, new_value):
        super().__init__()
        self.table = table_widget
        self.row = row
        self.column = column
        self.old_value = old_value
        self.new_value = new_value
        self.setText(f"Edit cell at ({row}, {column})")  # Deskripsi untuk command

    def undo(self):
        """Kembalikan ke nilai sebelumnya"""
        # Update tabel widget
        self.table.blockSignals(True)  # Hindari infinite loop
        item = QTableWidgetItem(str(self.old_value))
        self.table.setItem(self.row, self.column, item)
        # Update dataframe
        self.table.data.iloc[self.row, self.column] = self.old_value
        self.table.blockSignals(False)

    def redo(self):
        """Terapkan perubahan baru"""
        # Update tabel widget
        self.table.blockSignals(True)  # Hindari infinite loop
        item = QTableWidgetItem(str(self.new_value))
        self.table.setItem(self.row, self.column, item)
        # Update dataframe
        self.table.data.iloc[self.row, self.column] = self.new_value
        self.table.blockSignals(False)