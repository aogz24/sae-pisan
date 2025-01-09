from PyQt6.QtWidgets import QInputDialog

def add_row_before(parent, num_rows):
        """Add rows before the selected row in the specified sheet."""
        selection = parent.spreadsheet.selectionModel().selectedIndexes()
        if selection:
            selected_row = selection[0].row()
            parent.model1.addRowsBefore(parent.model1.index(selected_row, 0), num_rows)
            parent.update_table(1, parent.model1)
    
def add_row_after(parent, num_rows):
    """Add rows after the selected row in the specified sheet."""
    selection = parent.spreadsheet.selectionModel().selectedIndexes()
    if selection:
        selected_row = selection[0].row()
        parent.model1.addRowsAfter(parent.model1.index(selected_row, 0), num_rows)
        parent.update_table(1, parent.model1)

def show_add_row_before_dialog(parent):
        """Show a dialog to select which sheet to add a row to."""
        num_rows, ok = QInputDialog.getInt(parent, "Add Row", "Enter number of rows to add:", 1, 1)
        print(num_rows)
        if ok:
            for _ in range(num_rows):
                add_row_before(parent, num_rows)
    
def show_add_row_after_dialog(parent):
    """Show a dialog to select which sheet to add a row to."""
    num_rows, ok = QInputDialog.getInt(parent, "Add Row", "Enter number of rows to add:", 1, 1)
    if ok:
        for _ in range(num_rows):
            add_row_after(parent, num_rows)