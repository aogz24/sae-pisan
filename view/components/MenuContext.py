from service.table.AddRow import *
from service.table.AddColumn import *
from service.table.DeleteRow import *
from service.table.DeleteColumn import *
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QMenu

def show_context_menu(parent, position):
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