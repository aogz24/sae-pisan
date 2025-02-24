from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QAbstractItemView, QTextEdit, QComboBox, QLineEdit
from PyQt6.QtGui import QDoubleValidator, QIntValidator
from PyQt6.QtWidgets import QMessageBox

def assign_of_interest(parent):
    selected_indexes = parent.variables_list.selectedIndexes()
    if selected_indexes:
        for index in selected_indexes:
            if "[Numeric]" in index.data():
                parent.of_interest_var = [index.data()]
                parent.of_interest_model.setStringList(parent.of_interest_var)
                parent.variables_list.model().removeRow(selected_indexes[-1].row())  # Remove from variables list
                show_r_script(parent)

def assign_auxilary(parent):
    selected_indexes = parent.variables_list.selectedIndexes()
    if selected_indexes:
        new_vars = []
        for index in selected_indexes:
            if "[Numeric]" in index.data():
                new_vars.append(index.data())
        
        parent.auxilary_vars = list(set(parent.auxilary_vars + new_vars))  # Add new variables if they are different
        parent.auxilary_model.setStringList(parent.auxilary_vars)
        for index in sorted(selected_indexes, reverse=True):
            if "[Numeric]" in index.data():
                parent.variables_list.model().removeRow(index.row())  # Remove from variables list
        show_r_script(parent)

def assign_vardir(parent):
    selected_indexes = parent.variables_list.selectedIndexes()
    if selected_indexes:
        for index in selected_indexes:
            if "[Numeric]" in index.data():
                parent.vardir_var = [index.data()]
                parent.vardir_model.setStringList(parent.vardir_var)
                parent.variables_list.model().removeRow(selected_indexes[-1].row())  # Remove from variables list
                show_r_script(parent)

def assign_as_factor(parent):
    selected_indexes = parent.variables_list.selectedIndexes()
    if selected_indexes:
        new_vars = []
        for index in selected_indexes:
            new_vars.append(index.data())
        parent.as_factor_var = list(set(parent.as_factor_var + new_vars))  # Add new variables if they are different
        parent.as_factor_model.setStringList(parent.as_factor_var)
        for index in sorted(selected_indexes, reverse=True):
            parent.variables_list.model().removeRow(index.row())  # Remove from variables list
        show_r_script(parent)

def unassign_variable(parent):
    selected_indexes = parent.of_interest_list.selectedIndexes()
    if selected_indexes:
        selected_items = [index.data() for index in selected_indexes]
        parent.of_interest_var = [var for var in parent.of_interest_var if var not in selected_items]
        parent.of_interest_model.setStringList(parent.of_interest_var)
        parent.variables_list.model().insertRow(0)  # Add back to variables list
        parent.variables_list.model().setData(parent.variables_list.model().index(0), selected_items[0])
        show_r_script(parent)
        return

    selected_indexes = parent.auxilary_list.selectedIndexes()
    if selected_indexes:
        selected_items = [index.data() for index in selected_indexes]
        parent.auxilary_vars = [var for var in parent.auxilary_vars if var not in selected_items]
        parent.auxilary_model.setStringList(parent.auxilary_vars)
        for item in selected_items:
            parent.variables_list.model().insertRow(0)  # Add back to variables list
            parent.variables_list.model().setData(parent.variables_list.model().index(0), item)
        show_r_script(parent)
        return

    selected_indexes = parent.vardir_list.selectedIndexes()
    if selected_indexes:
        selected_items = [index.data() for index in selected_indexes]
        parent.vardir_var = [var for var in parent.vardir_var if var not in selected_items]
        parent.vardir_model.setStringList(parent.vardir_var)
        for item in selected_items:
            parent.variables_list.model().insertRow(0)  # Add back to variables list
            parent.variables_list.model().setData(parent.variables_list.model().index(0), item)
        show_r_script(parent)
        return

    selected_indexes = parent.as_factor_list.selectedIndexes()
    if selected_indexes:
        selected_items = [index.data() for index in selected_indexes]
        parent.as_factor_var = [var for var in parent.as_factor_var if var not in selected_items]
        parent.as_factor_model.setStringList(parent.as_factor_var)
        for item in selected_items:
            parent.variables_list.model().insertRow(0)  # Add back to variables list
            parent.variables_list.model().setData(parent.variables_list.model().index(0), item)
        show_r_script(parent)

def get_selected_variables(parent):
    return parent.of_interest_var, parent.auxilary_vars, parent.vardir_var, parent.as_factor_var

def generate_r_script(parent):
    of_interest_var = f'{parent.of_interest_var[0].split(" [")[0].replace(" ", "_")}' if parent.of_interest_var else '""'
    auxilary_vars = " + ".join([var.split(" [")[0].replace(" ", "_") for var in parent.auxilary_vars]) if parent.auxilary_vars else '""'
    vardir_var = f'{parent.vardir_var[0].split(" [")[0].replace(" ", "_")}' if parent.vardir_var else '""'
    as_factor_var = " + ".join([f'as.factor({var.split(" [")[0].replace(" ", "_")})' for var in parent.as_factor_var]) if parent.as_factor_var else '""'
    
    if (auxilary_vars=='""' or auxilary_vars is None) and as_factor_var=='""':
        formula = f'{of_interest_var} ~ 1'
    elif as_factor_var=='""':
        formula = f'{of_interest_var} ~ {auxilary_vars}'
    elif auxilary_vars=='""':
        formula = f'{of_interest_var} ~ {as_factor_var}'
    else:
        formula = f'{of_interest_var} ~ {auxilary_vars} + {as_factor_var}'

    r_script = f'names(data) <- gsub(" ", "_", names(data)); #Replace space with underscore\n'
    r_script += f'formula <- {formula}\n'
    r_script += f'vardir_var <- data["{vardir_var}"]\n'
    if parent.selection_method=="Stepwise":
        parent.selection_method = "both"
    if parent.selection_method and parent.selection_method != "None" and auxilary_vars:
        r_script += f'stepwise_model <- step(formula, direction="{parent.selection_method.lower()}")\n'
        r_script += f'final_formula <- formula(stepwise_model)\n'
        r_script += f'model<-mseFH(final_formula, vardir_var, method = "{parent.method}", data=data)'
    else:
        r_script += f'model<-mseFH(formula, vardir_var, method = "{parent.method}", data=data)'
    return r_script

def show_r_script(parent):
    r_script = generate_r_script(parent)
    parent.r_script_edit.setText(r_script)

def get_script(parent):
    return parent.r_script_edit.toPlainText()  

def show_options(parent):
    options_dialog = QDialog(parent)
    options_dialog.setWindowTitle("Options")

    layout = QVBoxLayout()

    method_label = QLabel("Method:")
    layout.addWidget(method_label)

    parent.method_selection = QComboBox()
    parent.method_selection.addItems(["ML", "REML", "FH"])
    parent.method_selection.setCurrentText("REML")
    layout.addWidget(parent.method_selection)

    button_layout = QHBoxLayout()
    ok_button = QPushButton("OK")
    cancel_button = QPushButton("Cancel")
    button_layout.addWidget(ok_button)
    button_layout.addWidget(cancel_button)

    layout.addLayout(button_layout)

    options_dialog.setLayout(layout)

    ok_button.clicked.connect(lambda: set_selection_method(parent, options_dialog))
    cancel_button.clicked.connect(options_dialog.reject)

    options_dialog.exec()

def set_selection_method(parent, dialog):
    # parent.selection_method = parent.method_combo.currentText()
    parent.method = parent.method_selection.currentText()
    dialog.accept()
    show_r_script(parent)
    
import unittest
from unittest.mock import MagicMock
from PyQt6.QtWidgets import QApplication, QMessageBox
from sae_eblup_area import assign_of_interest, assign_auxilary, assign_vardir, assign_as_factor, unassign_variable, generate_r_script, show_r_script

class TestSaeEblupArea(unittest.TestCase):
    def setUp(self):
        if not QApplication.instance():
            self.app = QApplication([])  # Required for creating PyQt widgets
        self.parent = MagicMock()
        self.parent.variables_list.selectedIndexes.return_value = []
        self.parent.of_interest_var = []
        self.parent.auxilary_vars = []
        self.parent.vardir_var = []
        self.parent.as_factor_var = []
        self.parent.of_interest_model = MagicMock()
        self.parent.auxilary_model = MagicMock()
        self.parent.vardir_model = MagicMock()
        self.parent.as_factor_model = MagicMock()
        self.parent.r_script_edit = MagicMock()
        self.parent.method = "REML"
        self.parent.selection_method = "None"


    def test_assign_of_interest_with_numeric(self):
        index = MagicMock()
        index.data.return_value = "variable1 [Numeric]"
        self.parent.variables_list.selectedIndexes.return_value = [index]
        
        assign_of_interest(self.parent)
        
        self.assertEqual(self.parent.of_interest_var, ["variable1 [Numeric]"])
        self.parent.of_interest_model.setStringList.assert_called_with(["variable1 [Numeric]"])
        self.parent.variables_list.model().removeRow.assert_called_once()

    def test_assign_of_interest_with_string(self):
        index = MagicMock()
        index.data.return_value = "variable1 [String]"
        self.parent.variables_list.selectedIndexes.return_value = [index]
        
        assign_of_interest(self.parent)
        
        self.assertEqual(self.parent.of_interest_var, [])
        self.parent.of_interest_model.setStringList.assert_not_called()
        self.parent.variables_list.model().removeRow.assert_not_called()
        self.assertFalse(self.parent.show_r_script.called)

    def test_assign_auxilary_with_numeric(self):
        index = MagicMock()
        index.data.return_value = "variable1 [Numeric]"
        self.parent.variables_list.selectedIndexes.return_value = [index]
        
        assign_auxilary(self.parent)
        
        self.assertEqual(self.parent.auxilary_vars, ["variable1 [Numeric]"])
        self.parent.auxilary_model.setStringList.assert_called_with(["variable1 [Numeric]"])
        self.parent.variables_list.model().removeRow.assert_called_once()

    def test_assign_auxilary_with_string(self):
        index = MagicMock()
        index.data.return_value = "variable1 [String]"
        self.parent.variables_list.selectedIndexes.return_value = [index]
        
        assign_auxilary(self.parent)
        
        self.assertEqual(self.parent.auxilary_vars, [])
        # self.parent.auxilary_model.setStringList.assert_not_called()
        self.parent.variables_list.model().removeRow.assert_not_called()
        self.assertFalse(self.parent.show_r_script.called)

    def test_generate_r_script(self):
        self.parent.of_interest_var = ["variable1 [Numeric]"]
        self.parent.auxilary_vars = ["variable2 [Numeric]"]
        self.parent.vardir_var = ["variable3 [Numeric]"]
        self.parent.as_factor_var = ["variable4 [String]"]
        
        r_script = generate_r_script(self.parent)
        
        expected_script = (
            'names(data) <- gsub(" ", "_", names(data)); #Replace space with underscore\n'
            'formula <- variable1 ~ variable2 + as.factor(variable4)\n'
            'vardir_var <- data["variable3"]\n'
            'model<-mseFH(formula, vardir_var, method = "REML", data=data)'
        )
        self.assertEqual(r_script, expected_script)

if __name__ == '__main__':
    unittest.main()
