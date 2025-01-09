from PyQt6.QtWidgets import QMessageBox

def delete_selected_columns(parent):
        """Delete selected columns in the spreadsheet."""
        selection = parent.spreadsheet.selectionModel().selectedIndexes()
        if selection:
            columns = sorted(set(index.column() for index in selection), reverse=True)
            for column in columns:
                parent.model1.deleteColumn(parent.model1.index(0, column))
            parent.update_table(1, parent.model1)

def confirm_delete_selected_columns(parent):
    """Show a confirmation dialog before deleting selected columns."""
    reply = QMessageBox.question(parent, 'Confirm Delete', 'Are you sure you want to delete the selected columns?',
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
    if reply == QMessageBox.StandardButton.Yes:
        delete_selected_columns(parent)