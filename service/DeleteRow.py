from PyQt6.QtWidgets import QMessageBox

def delete_selected_rows(parent):
        """Delete selected rows in the spreadsheet."""
        selection = parent.spreadsheet.selectionModel().selectedIndexes()
        if selection:
            rows = sorted(set(index.row() for index in selection), reverse=True)
            for row in rows:
                parent.model1.deleteRow(parent.model1.index(row, 0))
            parent.update_table(1, parent.model1)

def confirm_delete_selected_rows(parent):
        """Show a confirmation dialog before deleting selected rows."""
        reply = QMessageBox.question(parent, 'Confirm Delete', 'Are you sure you want to delete the selected rows?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            delete_selected_rows(parent)