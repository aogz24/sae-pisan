from service.table.AddRow import *
from service.table.AddColumn import *
from service.table.DeleteRow import *
from service.table.DeleteColumn import *
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QMenu

def show_context_menu(parent, position):
        """
        Displays a context menu at the given position within the parent widget.
        Parameters:
        parent (QWidget): The parent widget where the context menu will be displayed.
        position (QPoint): The position within the parent widget where the context menu will appear.
        The context menu provides the following options:
        - Add Row Before: Adds a new row before the selected row(s).
        - Add Row After: Adds a new row after the selected row(s).
        - Add Column Before: Adds a new column before the selected column(s).
        - Add Column After: Adds a new column after the selected column(s).
        - Delete Row: Deletes the selected row(s).
        - Delete Column: Deletes the selected column(s).
        The actions are enabled only if there is a selection in the spreadsheet.
        """
        
        context_menu = QMenu(parent)

        selection = parent.spreadsheet.selectionModel().selectedIndexes()
        has_selection = bool(selection)

        add_row_before_action = QAction("Add Row Before", parent)
        add_row_before_action.triggered.connect(lambda: show_add_row_before_dialog(parent))
        add_row_before_action.setEnabled(has_selection)
        context_menu.addAction(add_row_before_action)

        add_row_after_action = QAction("Add Row After", parent)
        add_row_after_action.triggered.connect(lambda: show_add_row_after_dialog(parent))
        add_row_after_action.setEnabled(has_selection)
        context_menu.addAction(add_row_after_action)

        add_column_before_action = QAction("Add Column Before", parent)
        add_column_before_action.triggered.connect(lambda: show_add_column_before_dialog(parent))
        add_column_before_action.setEnabled(has_selection)
        context_menu.addAction(add_column_before_action)

        add_column_after_action = QAction("Add Column After", parent)
        add_column_after_action.triggered.connect(lambda: show_add_column_after_dialog(parent))
        add_column_after_action.setEnabled(has_selection)
        context_menu.addAction(add_column_after_action)

        delete_row_action = QAction("Delete Row", parent)
        delete_row_action.triggered.connect(lambda : confirm_delete_selected_rows(parent))
        delete_row_action.setEnabled(has_selection)
        context_menu.addAction(delete_row_action)

        delete_column_action = QAction("Delete Column", parent)
        delete_column_action.triggered.connect(lambda : confirm_delete_selected_columns(parent))
        delete_column_action.setEnabled(has_selection)
        context_menu.addAction(delete_column_action)
        
        context_menu.exec(parent.spreadsheet.viewport().mapToGlobal(position))