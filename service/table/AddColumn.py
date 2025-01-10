from PyQt6.QtWidgets import QInputDialog
from model.TableModel import TableModel
import polars as pl

def add_column_before(parent, num_columns):
    """Add columns before the selected column in the specified sheet."""
    selection = parent.spreadsheet.selectionModel().selectedIndexes()
    if selection:
        selected_column = selection[0].column()
        parent.model1.addColumnBefore(parent.model1.index(0, selected_column), num_columns)
        parent.update_table(1, parent.model1)

def add_column_after(parent, num_columns):
    """Add columns after the selected column in the specified sheet."""
    selection = parent.spreadsheet.selectionModel().selectedIndexes()
    if selection:
        selected_column = selection[0].column()
        parent.model1.addColumnAfter(parent.model1.index(0, selected_column), num_columns)
        parent.update_table(1, parent.model1)
        
            
def show_add_column_before_dialog(parent):
    """Show a dialog to select which sheet to add a row to."""
    num_rows, ok = QInputDialog.getInt(parent, "Add Row", "Enter number of rows to add:", 1, 1)
    if ok:
        for _ in range(num_rows):
            add_column_before(parent, num_rows)

def show_add_column_after_dialog(parent):
    """Show a dialog to select which sheet to add a row to."""
    num_rows, ok = QInputDialog.getInt(parent, "Add Row", "Enter number of rows to add:", 1, 1)
    if ok:
        for _ in range(num_rows):
            add_column_after(parent, num_rows)