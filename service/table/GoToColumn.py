from PyQt6.QtCore import Qt, QSize, QModelIndex, QItemSelectionModel 

def go_to_start_column(parent):
        """Move the selection to the start column while keeping the row the same."""
        if parent.tab_widget.currentIndex() == 0:
            selection = parent.spreadsheet.selectionModel().selectedIndexes()
            if selection:
                start_row = selection[0].row()
                parent.spreadsheet.setCurrentIndex(parent.model1.index(start_row, 0))
                parent.spreadsheet.selectionModel().select(parent.model1.index(start_row, 0), QItemSelectionModel.SelectionFlag.ClearAndSelect)
        elif parent.tab_widget.currentIndex() == 1:
            selection = parent.table_view2.selectionModel().selectedIndexes()
            if selection:
                start_row = selection[0].row()
                parent.table_view2.setCurrentIndex(parent.model2.index(start_row, 0))
                parent.table_view2.selectionModel().select(parent.model2.index(start_row, 0), QItemSelectionModel.SelectionFlag.ClearAndSelect)

def go_to_end_column(parent):
    """Move the selection to the end column while keeping the row the same."""
    if parent.tab_widget.currentIndex() == 0:
        selection = parent.spreadsheet.selectionModel().selectedIndexes()
        if selection:
            start_row = selection[0].row()
            end_col = parent.model1.columnCount(parent.model1.index(0, 0)) - 1
            parent.spreadsheet.setCurrentIndex(parent.model1.index(start_row, end_col))
            parent.spreadsheet.selectionModel().select(parent.model1.index(start_row, end_col), QItemSelectionModel.SelectionFlag.ClearAndSelect)
    elif parent.tab_widget.currentIndex() == 1:
        selection = parent.table_view2.selectionModel().selectedIndexes()
        if selection:
            start_row = selection[0].row()
            end_col = parent.model2.columnCount(parent.model2.index(0, 0)) - 1
            parent.table_view2.setCurrentIndex(parent.model2.index(start_row, end_col))
            parent.table_view2.selectionModel().select(parent.model2.index(start_row, end_col), QItemSelectionModel.SelectionFlag.ClearAndSelect)