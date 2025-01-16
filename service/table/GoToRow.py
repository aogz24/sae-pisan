from PyQt6.QtCore import QModelIndex, QItemSelectionModel 
def go_to_start_row(parent):
        """Move the selection to the start row while keeping the column the same."""
        selection = parent.spreadsheet.selectionModel().selectedIndexes()
        if selection:
            start_col = selection[0].column()
            parent.spreadsheet.setCurrentIndex(parent.model1.index(0, start_col))
            parent.spreadsheet.selectionModel().select(parent.model1.index(0, start_col), QItemSelectionModel.SelectionFlag.ClearAndSelect)

def go_to_end_row(parent):
    """Move the selection to the end row while keeping the column the same."""
    if parent.tab_widget.currentIndex() == 0:
        selection = parent.spreadsheet.selectionModel().selectedIndexes()
        if selection:
            start_col = selection[0].column()
            end_row = parent.model1.rowCount(QModelIndex()) - 1
            parent.spreadsheet.setCurrentIndex(parent.model1.index(end_row, start_col))
            parent.spreadsheet.selectionModel().select(parent.model1.index(end_row, start_col), QItemSelectionModel.SelectionFlag.ClearAndSelect)
    elif parent.tab_widget.currentIndex() == 1:
        selection = parent.table_view2.selectionModel().selectedIndexes()
        if selection:
            start_col = selection[0].column()
            end_row = parent.model2.rowCount(QModelIndex()) - 1
            parent.table_view2.setCurrentIndex(parent.model2.index(end_row, start_col))
            parent.table_view2.selectionModel().select(parent.model2.index(end_row, start_col), QItemSelectionModel.SelectionFlag.ClearAndSelect)