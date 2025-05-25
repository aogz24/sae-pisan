from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QAbstractItemView, QTextEdit, QComboBox, QLineEdit
from PyQt6.QtGui import QDoubleValidator, QIntValidator
from PyQt6.QtWidgets import QMessageBox

def assign_of_interest(parent):
    selected_indexes = parent.variables_list.selectedIndexes()
    if selected_indexes:
        all_string = True
        for index in selected_indexes:
            type_of_var = index.data().split(" [")[1].replace("]", "")
            if type_of_var != "String":
                all_string = False
                parent.of_interest_var = [index.data()]
                parent.of_interest_model.setStringList(parent.of_interest_var)
                parent.variables_list.model().removeRow(selected_indexes[-1].row())  # Remove from variables list
                parent.show_r_script()
                break
        if all_string:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText("All selected variables are of type String. Variable of interest must be of type Numeric.")
            msg.setWindowTitle("Warning")
            msg.exec()

def assign_auxilary(parent):
    selected_indexes = parent.variables_list.selectedIndexes()
    if selected_indexes:
        new_vars = []
        for index in selected_indexes:
            type_of_var = index.data().split(" [")[1].replace("]", "")
            if type_of_var != "String":
                new_vars.append(index.data())
        if not new_vars:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText("No valid numeric variables selected. Please select at least one numeric variable.")
            msg.setWindowTitle("Warning")
            msg.exec()
            return
        parent.auxilary_vars = list(set(parent.auxilary_vars + new_vars))  # Add new variables if they are different
        parent.auxilary_model.setStringList(parent.auxilary_vars)
        for index in sorted(selected_indexes, reverse=True):
            parent.variables_list.model().removeRow(index.row())  # Remove from variables list
        parent.show_r_script()

def assign_index(parent):
    selected_indexes = parent.variables_list.selectedIndexes()
    if selected_indexes:
        for index in selected_indexes:
            parent.index_var = [index.data()]
            parent.index_model.setStringList(parent.index_var)
            parent.variables_list.model().removeRow(selected_indexes[-1].row())  # Remove from variables list
            parent.show_r_script()
            break

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
        parent.show_r_script()
        
def assign_domains(parent):
    selected_indexes = parent.variables_list.selectedIndexes()
    if selected_indexes:
        parent.domain_var = [selected_indexes[0].data()]  # Only one variable
        parent.domain_model.setStringList(parent.domain_var)
        parent.variables_list.model().removeRow(selected_indexes[0].row())  # Remove from variables list
        parent.show_r_script()

def assign_aux_mean(parent):
    selected_indexes = parent.variables_list.selectedIndexes()
    if selected_indexes:
        new_vars = []
        for index in selected_indexes:
            type_of_var = index.data().split(" [")[1].replace("]", "")
            if type_of_var != "String":
                new_vars.append(index.data())
        if not new_vars:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText("No valid numeric variables selected. Please select at least one numeric variable.")
            msg.setWindowTitle("Warning")
            msg.exec()
            return
        parent.aux_mean_vars = list(set(parent.aux_mean_vars + new_vars))  # Add new variables if they are different
        parent.aux_mean_model.setStringList(parent.aux_mean_vars)
        for index in sorted(selected_indexes, reverse=True):
            parent.variables_list.model().removeRow(index.row())  # Remove from variables list
        parent.show_r_script()

def assign_population_sample_size(parent):
    selected_indexes = parent.variables_list.selectedIndexes()
    if selected_indexes:
        parent.population_sample_size_var = [selected_indexes[0].data()]  # Only one variable
        parent.population_sample_size_model.setStringList(parent.population_sample_size_var)
        parent.variables_list.model().removeRow(selected_indexes[0].row())  # Remove from variables list
        parent.show_r_script()

def unassign_variable(parent):
    selected_indexes = parent.of_interest_list.selectedIndexes()
    if selected_indexes:
        selected_items = [index.data() for index in selected_indexes]
        parent.of_interest_var = [var for var in parent.of_interest_var if var not in selected_items]
        parent.of_interest_model.setStringList(parent.of_interest_var)
        for item in selected_items:
            parent.variables_list.model().insertRow(0)  # Add back to variables list
            parent.variables_list.model().setData(parent.variables_list.model().index(0), item)
        parent.show_r_script()
        return

    selected_indexes = parent.auxilary_list.selectedIndexes()
    if selected_indexes:
        selected_items = [index.data() for index in selected_indexes]
        parent.auxilary_vars = [var for var in parent.auxilary_vars if var not in selected_items]
        parent.auxilary_model.setStringList(parent.auxilary_vars)
        for item in selected_items:
            parent.variables_list.model().insertRow(0)  # Add back to variables list
            parent.variables_list.model().setData(parent.variables_list.model().index(0), item)
        parent.show_r_script()
        return

    selected_indexes = parent.index_list.selectedIndexes()
    if selected_indexes:
        selected_items = [index.data() for index in selected_indexes]
        parent.index_var = [var for var in parent.index_var if var not in selected_items]
        parent.index_model.setStringList(parent.index_var)
        for item in selected_items:
            parent.variables_list.model().insertRow(0)  # Add back to variables list
            parent.variables_list.model().setData(parent.variables_list.model().index(0), item)
        parent.show_r_script()
        return

    selected_indexes = parent.as_factor_list.selectedIndexes()
    if selected_indexes:
        selected_items = [index.data() for index in selected_indexes]
        parent.as_factor_var = [var for var in parent.as_factor_var if var not in selected_items]
        parent.as_factor_model.setStringList(parent.as_factor_var)
        for item in selected_items:
            parent.variables_list.model().insertRow(0)  # Add back to variables list
            parent.variables_list.model().setData(parent.variables_list.model().index(0), item)
        parent.show_r_script()
        return

    selected_indexes = parent.domain_list.selectedIndexes()
    if selected_indexes:
        selected_items = [index.data() for index in selected_indexes]
        parent.domain_var = [var for var in parent.domain_var if var not in selected_items]
        parent.domain_model.setStringList(parent.domain_var)
        for item in selected_items:
            parent.variables_list.model().insertRow(0)  # Add back to variables list
            parent.variables_list.model().setData(parent.variables_list.model().index(0), item)
        parent.show_r_script()
        return

    selected_indexes = parent.auxilary_vars_mean_list.selectedIndexes()
    if selected_indexes:
        selected_items = [index.data() for index in selected_indexes]
        parent.aux_mean_vars = [var for var in parent.aux_mean_vars if var not in selected_items]
        parent.aux_mean_model.setStringList(parent.aux_mean_vars)
        for item in selected_items:
            parent.variables_list.model().insertRow(0)  # Add back to variables list
            parent.variables_list.model().setData(parent.variables_list.model().index(0), item)
        parent.show_r_script()
        return

    selected_indexes = parent.population_sample_size_list.selectedIndexes()
    if selected_indexes:
        selected_items = [index.data() for index in selected_indexes]
        parent.population_sample_size_var = [var for var in parent.population_sample_size_var if var not in selected_items]
        parent.population_sample_size_model.setStringList(parent.population_sample_size_var)
        for item in selected_items:
            parent.variables_list.model().insertRow(0)  # Add back to variables list
            parent.variables_list.model().setData(parent.variables_list.model().index(0), item)
        parent.show_r_script()

def get_selected_variables(parent):
    return parent.of_interest_var, parent.auxilary_vars, parent.vardir_var, parent.as_factor_var

def generate_r_script(parent):
    of_interest_var = f'{parent.of_interest_var[0].split(" [")[0].replace(" ", "_")}' if parent.of_interest_var else '""'
    auxilary_vars = " + ".join([var.split(" [")[0].replace(" ", "_") for var in parent.auxilary_vars]) if parent.auxilary_vars else '""'
    as_factor_var = " + ".join([f'as.factor({var.split(" [")[0].replace(" ", "_")})' for var in parent.as_factor_var]) if parent.as_factor_var else '""'
    index_var = f'{parent.index_var[0].split(" [")[0].replace(" ", "_")}' if parent.index_var else '""'
    aux_mean_vars = ",".join([f'{var.split(" [")[0].replace(" ", "_")}' for var in parent.aux_mean_vars]) if parent.aux_mean_vars else '""'
    population_sample_size_var = f'{parent.population_sample_size_var[0].split(" [")[0].replace(" ", "_")}' if parent.population_sample_size_var else '""'
    domain_var = f'{parent.domain_var[0].split(" [")[0].replace(" ", "_")}' if parent.domain_var else '""'
    
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
    r_script += f'Xmeans <- with(data, data.frame({index_var},{aux_mean_vars}))\n'
    r_script += f'Popn <- with(data, data.frame({index_var},{population_sample_size_var}))\n'
    r_script += f'Xmeans <- na.omit(Xmeans)\n'
    r_script += f'Popn <- na.omit(Popn)\n'
    r_script += f'Popn <- Popn[complete.cases(Popn), ]\n'
    r_script += f'Xmeans <- Xmeans[complete.cases(Xmeans), ]\n'
    r_script += f'domains=Xmeans[,1]\n'
    
    if parent.selection_method=="Stepwise":
        parent.selection_method = "both"
    if parent.selection_method and parent.selection_method != "None" and auxilary_vars:
        r_script += f'stepwise_model <- step(formula, direction='
    if parent.selection_method=="Stepwise":
        parent.selection_method = "both"
    if parent.selection_method and parent.selection_method != "None" and auxilary_vars:
        r_script += f'stepwise_model <- step(formula, direction="{parent.selection_method.lower()}")\n'
        r_script += f'final_formula <- formula(stepwise_model)\n'
        r_script += f'model<-pbmseBHF(final_formula, dom={domain_var}, selectdom=domains, meanxpop=Xmeans, popnsize=Popn, B={parent.bootstrap}, method = "{parent.method}", data=data)'
    else:
        r_script += f'model<-pbmseBHF(formula,dom={domain_var}, selectdom=domains, meanxpop=Xmeans, popnsize=Popn, B={parent.bootstrap}, method = "{parent.method}", data=data)'
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
    
    bootstrap_label = QLabel("Bootstrap:")
    layout.addWidget(bootstrap_label)
    
    parent.bootstrap_edit = QLineEdit()
    parent.bootstrap_edit.setValidator(QIntValidator())
    parent.bootstrap_edit.setText("50")
    layout.addWidget(parent.bootstrap_edit)
    

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
    parent.bootstrap = parent.bootstrap_edit.text()
    dialog.accept()
    show_r_script(parent)

import unittest
from unittest.mock import MagicMock
import sys
from PyQt6.QtWidgets import QApplication

class TestUnassignVariable(unittest.TestCase):

    def setUp(self):
        self.parent = MagicMock()
        self.parent.of_interest_var = ["var1 [Numeric]", "var2 [Numeric]"]
        self.parent.auxilary_vars = ["var3 [Numeric]", "var4 [Numeric]"]
        self.parent.index_var = ["var5 [Numeric]"]
        self.parent.as_factor_var = ["var6 [String]"]
        self.parent.domain_var = ["var7 [Numeric]"]
        self.parent.aux_mean_vars = ["var8 [Numeric]"]
        self.parent.population_sample_size_var = ["var9 [Numeric]"]

        self.parent.of_interest_list.selectedIndexes.return_value = [MagicMock(data=MagicMock(return_value="var1 [Numeric]"))]
        self.parent.auxilary_list.selectedIndexes.return_value = []
        self.parent.index_list.selectedIndexes.return_value = []
        self.parent.as_factor_list.selectedIndexes.return_value = []
        self.parent.domain_list.selectedIndexes.return_value = []
        self.parent.auxilary_vars_mean_list.selectedIndexes.return_value = []
        self.parent.population_sample_size_list.selectedIndexes.return_value = []

    def test_unassign_of_interest_variable(self):
        """
        Test the unassignment of a variable of interest from the parent object.

        This test verifies that:
        - The specified variable ("var1 [Numeric]") is removed from the parent's list of variables of interest.
        - The model's string list is updated accordingly.
        - The variable is reinserted into the variables list model.
        - The data in the variables list model is updated.
        - The R script display function is called to reflect the changes.

        Komentar:
        Fungsi ini memastikan bahwa ketika variabel of interest di-unassign, seluruh komponen terkait diupdate dengan benar, termasuk tampilan dan model data.
        """
        unassign_variable(self.parent)
        self.assertNotIn("var1 [Numeric]", self.parent.of_interest_var)
        self.parent.of_interest_model.setStringList.assert_called_with(self.parent.of_interest_var)
        self.parent.variables_list.model().insertRow.assert_called()
        self.parent.variables_list.model().setData.assert_called()
        self.parent.show_r_script.assert_called()

    def test_unassign_auxilary_variable(self):
        self.parent.of_interest_list.selectedIndexes.return_value = []
        self.parent.auxilary_list.selectedIndexes.return_value = [MagicMock(data=MagicMock(return_value="var3 [Numeric]"))]
        unassign_variable(self.parent)
        self.assertNotIn("var3 [Numeric]", self.parent.auxilary_vars)
        self.parent.auxilary_model.setStringList.assert_called_with(self.parent.auxilary_vars)
        self.parent.variables_list.model().insertRow.assert_called()
        self.parent.variables_list.model().setData.assert_called()
        self.parent.show_r_script.assert_called()

    def test_unassign_index_variable(self):
        self.parent.of_interest_list.selectedIndexes.return_value = []
        self.parent.index_list.selectedIndexes.return_value = [MagicMock(data=MagicMock(return_value="var5 [Numeric]"))]
        unassign_variable(self.parent)
        self.assertNotIn("var5 [Numeric]", self.parent.index_var)
        self.parent.index_model.setStringList.assert_called_with(self.parent.index_var)
        self.parent.variables_list.model().insertRow.assert_called()
        self.parent.variables_list.model().setData.assert_called()
        self.parent.show_r_script.assert_called()

    def test_unassign_as_factor_variable(self):
        self.parent.of_interest_list.selectedIndexes.return_value = []
        self.parent.as_factor_list.selectedIndexes.return_value = [MagicMock(data=MagicMock(return_value="var6 [String]"))]
        unassign_variable(self.parent)
        self.assertNotIn("var6 [String]", self.parent.as_factor_var)
        self.parent.as_factor_model.setStringList.assert_called_with(self.parent.as_factor_var)
        self.parent.variables_list.model().insertRow.assert_called()
        self.parent.variables_list.model().setData.assert_called()
        self.parent.show_r_script.assert_called()

    def test_unassign_domain_variable(self):
        self.parent.of_interest_list.selectedIndexes.return_value = []
        self.parent.domain_list.selectedIndexes.return_value = [MagicMock(data=MagicMock(return_value="var7 [Numeric]"))]
        unassign_variable(self.parent)
        self.assertNotIn("var7 [Numeric]", self.parent.domain_var)
        self.parent.domain_model.setStringList.assert_called_with(self.parent.domain_var)
        self.parent.variables_list.model().insertRow.assert_called()
        self.parent.variables_list.model().setData.assert_called()
        self.parent.show_r_script.assert_called()

    def test_unassign_aux_mean_variable(self):
        self.parent.of_interest_list.selectedIndexes.return_value = []
        self.parent.auxilary_vars_mean_list.selectedIndexes.return_value = [MagicMock(data=MagicMock(return_value="var8 [Numeric]"))]
        unassign_variable(self.parent)
        self.assertNotIn("var8 [Numeric]", self.parent.aux_mean_vars)
        self.parent.aux_mean_model.setStringList.assert_called_with(self.parent.aux_mean_vars)
        self.parent.variables_list.model().insertRow.assert_called()
        self.parent.variables_list.model().setData.assert_called()
        self.parent.show_r_script.assert_called()

    def test_unassign_population_sample_size_variable(self):
        self.parent.of_interest_list.selectedIndexes.return_value = []
        self.parent.population_sample_size_list.selectedIndexes.return_value = [MagicMock(data=MagicMock(return_value="var9 [Numeric]"))]
        unassign_variable(self.parent)
        self.assertNotIn("var9 [Numeric]", self.parent.population_sample_size_var)
        self.parent.population_sample_size_model.setStringList.assert_called_with(self.parent.population_sample_size_var)
        self.parent.variables_list.model().insertRow.assert_called()
        self.parent.variables_list.model().setData.assert_called()
        self.parent.show_r_script.assert_called()
        
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
        self.parent.of_interest_var = []
        with unittest.mock.patch("PyQt6.QtWidgets.QMessageBox.exec") as mock_exec:
            assign_of_interest(self.parent)
            self.assertEqual(self.parent.of_interest_var, [])
            self.parent.of_interest_model.setStringList.assert_not_called()
            self.parent.variables_list.model().removeRow.assert_not_called()
            self.assertFalse(self.parent.show_r_script.called)
            mock_exec.assert_called_once()

    def test_assign_auxilary_with_numeric(self):
        index = MagicMock()
        index.data.return_value = "variable1 [Numeric]"
        self.parent.variables_list.selectedIndexes.return_value = [index]
        assign_auxilary(self.parent)
        self.assertIn("variable1 [Numeric]", self.parent.auxilary_vars)
        self.parent.auxilary_model.setStringList.assert_called_with(self.parent.auxilary_vars)
        self.parent.variables_list.model().removeRow.assert_called_once()

    def test_assign_auxilary_with_string(self):
        index = MagicMock()
        index.data.return_value = "variable1 [String]"
        self.parent.variables_list.selectedIndexes.return_value = [index]
        self.parent.auxilary_vars = []
        with unittest.mock.patch("PyQt6.QtWidgets.QMessageBox.exec") as mock_exec:
            assign_auxilary(self.parent)
            self.assertEqual(self.parent.auxilary_vars, [])
            self.parent.variables_list.model().removeRow.assert_not_called()
            self.assertFalse(self.parent.show_r_script.called)
            mock_exec.assert_called_once()

    def test_assign_index(self):
        index = MagicMock()
        index.data.return_value = "variable1 [Numeric]"
        self.parent.variables_list.selectedIndexes.return_value = [index]
        assign_index(self.parent)
        self.assertEqual(self.parent.index_var, ["variable1 [Numeric]"])
        self.parent.index_model.setStringList.assert_called_with(["variable1 [Numeric]"])
        self.parent.variables_list.model().removeRow.assert_called_once()

    def test_assign_as_factor(self):
        index = MagicMock()
        index.data.return_value = "variable1 [String]"
        self.parent.variables_list.selectedIndexes.return_value = [index]
        assign_as_factor(self.parent)
        self.assertIn("variable1 [String]", self.parent.as_factor_var)
        self.parent.as_factor_model.setStringList.assert_called_with(self.parent.as_factor_var)
        self.parent.variables_list.model().removeRow.assert_called_once()

    def test_assign_domains(self):
        index = MagicMock()
        index.data.return_value = "variable1 [Numeric]"
        self.parent.variables_list.selectedIndexes.return_value = [index]
        assign_domains(self.parent)
        self.assertEqual(self.parent.domain_var, ["variable1 [Numeric]"])
        self.parent.domain_model.setStringList.assert_called_with(["variable1 [Numeric]"])
        self.parent.variables_list.model().removeRow.assert_called_once()

    def test_assign_aux_mean_with_numeric(self):
        index = MagicMock()
        index.data.return_value = "variable1 [Numeric]"
        self.parent.variables_list.selectedIndexes.return_value = [index]
        assign_aux_mean(self.parent)
        self.assertIn("variable1 [Numeric]", self.parent.aux_mean_vars)
        self.parent.aux_mean_model.setStringList.assert_called_with(self.parent.aux_mean_vars)
        self.parent.variables_list.model().removeRow.assert_called_once()

    def test_assign_aux_mean_with_string(self):
        index = MagicMock()
        index.data.return_value = "variable1 [String]"
        self.parent.variables_list.selectedIndexes.return_value = [index]
        self.parent.aux_mean_vars = []
        with unittest.mock.patch("PyQt6.QtWidgets.QMessageBox.exec") as mock_exec:
            assign_aux_mean(self.parent)
            self.assertEqual(self.parent.aux_mean_vars, [])
            self.parent.variables_list.model().removeRow.assert_not_called()
            self.assertFalse(self.parent.show_r_script.called)
            mock_exec.assert_called_once()

    def test_assign_population_sample_size(self):
        index = MagicMock()
        index.data.return_value = "variable1 [Numeric]"
        self.parent.variables_list.selectedIndexes.return_value = [index]
        assign_population_sample_size(self.parent)
        self.assertEqual(self.parent.population_sample_size_var, ["variable1 [Numeric]"])
        self.parent.population_sample_size_model.setStringList.assert_called_with(["variable1 [Numeric]"])
        self.parent.variables_list.model().removeRow.assert_called_once()

    def test_unassign_variable_of_interest(self):
        self.parent.of_interest_var = ["variable1 [Numeric]"]
        index = MagicMock()
        index.data.return_value = "variable1 [Numeric]"
        self.parent.of_interest_list.selectedIndexes.return_value = [index]
        self.parent.auxilary_list.selectedIndexes.return_value = []
        self.parent.index_list.selectedIndexes.return_value = []
        self.parent.as_factor_list.selectedIndexes.return_value = []
        self.parent.domain_list.selectedIndexes.return_value = []
        self.parent.auxilary_vars_mean_list.selectedIndexes.return_value = []
        self.parent.population_sample_size_list.selectedIndexes.return_value = []
        unassign_variable(self.parent)
        self.assertEqual(self.parent.of_interest_var, [])
        self.parent.of_interest_model.setStringList.assert_called_with([])
        self.parent.variables_list.model().insertRow.assert_called_once()
        self.parent.variables_list.model().setData.assert_called()
        self.parent.show_r_script.assert_called()

    def test_unassign_variable_auxilary(self):
        self.parent.of_interest_list.selectedIndexes.return_value = []
        self.parent.auxilary_vars = ["variable1 [Numeric]"]
        index = MagicMock()
        index.data.return_value = "variable1 [Numeric]"
        self.parent.auxilary_list.selectedIndexes.return_value = [index]
        self.parent.index_list.selectedIndexes.return_value = []
        self.parent.as_factor_list.selectedIndexes.return_value = []
        self.parent.domain_list.selectedIndexes.return_value = []
        self.parent.auxilary_vars_mean_list.selectedIndexes.return_value = []
        self.parent.population_sample_size_list.selectedIndexes.return_value = []
        unassign_variable(self.parent)
        self.assertEqual(self.parent.auxilary_vars, [])
        self.parent.auxilary_model.setStringList.assert_called_with([])
        self.parent.variables_list.model().insertRow.assert_called_once()
        self.parent.variables_list.model().setData.assert_called()
        self.parent.show_r_script.assert_called()

    def test_unassign_variable_index(self):
        self.parent.of_interest_list.selectedIndexes.return_value = []
        self.parent.auxilary_list.selectedIndexes.return_value = []
        self.parent.index_var = ["variable1 [Numeric]"]
        index = MagicMock()
        index.data.return_value = "variable1 [Numeric]"
        self.parent.index_list.selectedIndexes.return_value = [index]
        self.parent.as_factor_list.selectedIndexes.return_value = []
        self.parent.domain_list.selectedIndexes.return_value = []
        self.parent.auxilary_vars_mean_list.selectedIndexes.return_value = []
        self.parent.population_sample_size_list.selectedIndexes.return_value = []
        unassign_variable(self.parent)
        self.assertEqual(self.parent.index_var, [])
        self.parent.index_model.setStringList.assert_called_with([])
        self.parent.variables_list.model().insertRow.assert_called_once()
        self.parent.variables_list.model().setData.assert_called()
        self.parent.show_r_script.assert_called()

    def test_unassign_variable_as_factor(self):
        self.parent.of_interest_list.selectedIndexes.return_value = []
        self.parent.auxilary_list.selectedIndexes.return_value = []
        self.parent.index_list.selectedIndexes.return_value = []
        self.parent.as_factor_var = ["variable1 [String]"]
        index = MagicMock()
        index.data.return_value = "variable1 [String]"
        self.parent.as_factor_list.selectedIndexes.return_value = [index]
        self.parent.domain_list.selectedIndexes.return_value = []
        self.parent.auxilary_vars_mean_list.selectedIndexes.return_value = []
        self.parent.population_sample_size_list.selectedIndexes.return_value = []
        unassign_variable(self.parent)
        self.assertEqual(self.parent.as_factor_var, [])
        self.parent.as_factor_model.setStringList.assert_called_with([])
        self.parent.variables_list.model().insertRow.assert_called_once()
        self.parent.variables_list.model().setData.assert_called()
        self.parent.show_r_script.assert_called()

    def test_unassign_variable_domain(self):
        self.parent.of_interest_list.selectedIndexes.return_value = []
        self.parent.auxilary_list.selectedIndexes.return_value = []
        self.parent.index_list.selectedIndexes.return_value = []
        self.parent.as_factor_list.selectedIndexes.return_value = []
        self.parent.domain_var = ["variable1 [Numeric]"]
        index = MagicMock()
        index.data.return_value = "variable1 [Numeric]"
        self.parent.domain_list.selectedIndexes.return_value = [index]
        self.parent.auxilary_vars_mean_list.selectedIndexes.return_value = []
        self.parent.population_sample_size_list.selectedIndexes.return_value = []
        unassign_variable(self.parent)
        self.assertEqual(self.parent.domain_var, [])
        self.parent.domain_model.setStringList.assert_called_with([])
        self.parent.variables_list.model().insertRow.assert_called_once()
        self.parent.variables_list.model().setData.assert_called()
        self.parent.show_r_script.assert_called()

    def test_unassign_variable_aux_mean(self):
        self.parent.of_interest_list.selectedIndexes.return_value = []
        self.parent.auxilary_list.selectedIndexes.return_value = []
        self.parent.index_list.selectedIndexes.return_value = []
        self.parent.as_factor_list.selectedIndexes.return_value = []
        self.parent.domain_list.selectedIndexes.return_value = []
        self.parent.aux_mean_vars = ["variable1 [Numeric]"]
        index = MagicMock()
        index.data.return_value = "variable1 [Numeric]"
        self.parent.auxilary_vars_mean_list.selectedIndexes.return_value = [index]
        self.parent.population_sample_size_list.selectedIndexes.return_value = []
        unassign_variable(self.parent)
        self.assertEqual(self.parent.aux_mean_vars, [])
        self.parent.aux_mean_model.setStringList.assert_called_with([])
        self.parent.variables_list.model().insertRow.assert_called_once()
        self.parent.variables_list.model().setData.assert_called()
        self.parent.show_r_script.assert_called()

    def test_unassign_variable_population_sample_size(self):
        self.parent.of_interest_list.selectedIndexes.return_value = []
        self.parent.auxilary_list.selectedIndexes.return_value = []
        self.parent.index_list.selectedIndexes.return_value = []
        self.parent.as_factor_list.selectedIndexes.return_value = []
        self.parent.domain_list.selectedIndexes.return_value = []
        self.parent.auxilary_vars_mean_list.selectedIndexes.return_value = []
        self.parent.population_sample_size_var = ["variable1 [Numeric]"]
        index = MagicMock()
        index.data.return_value = "variable1 [Numeric]"
        self.parent.population_sample_size_list.selectedIndexes.return_value = [index]
        unassign_variable(self.parent)
        self.assertEqual(self.parent.population_sample_size_var, [])
        self.parent.population_sample_size_model.setStringList.assert_called_with([])
        self.parent.variables_list.model().insertRow.assert_called_once()
        self.parent.variables_list.model().setData.assert_called()
        self.parent.show_r_script.assert_called()

    def test_get_selected_variables(self):
        self.parent.of_interest_var = ["variable1 [Numeric]"]
        self.parent.auxilary_vars = ["variable2 [Numeric]"]
        self.parent.vardir_var = ["variable3 [Numeric]"]
        self.parent.as_factor_var = ["variable4 [String]"]
        result = get_selected_variables(self.parent)
        self.assertEqual(result, (
            ["variable1 [Numeric]"],
            ["variable2 [Numeric]"],
            ["variable3 [Numeric]"],
            ["variable4 [String]"],
        ))

    def test_generate_r_script(self):
        self.parent.of_interest_var = ["y [Numeric]"]
        self.parent.auxilary_vars = ["x1 [Numeric]", "x2 [Numeric]"]
        self.parent.as_factor_var = ["f1 [String]"]
        self.parent.index_var = ["idx [Numeric]"]
        self.parent.aux_mean_vars = ["mx1 [Numeric]"]
        self.parent.population_sample_size_var = ["pop [Numeric]"]
        self.parent.domain_var = ["dom [Numeric]"]
        self.parent.selection_method = "None"
        self.parent.method = "REML"
        self.parent.bootstrap = "100"
        script = generate_r_script(self.parent)
        self.assertIn('formula <- y ~ x1 + x2 + as.factor(f1)', script)
        self.assertIn('model<-pbmseBHF(formula,dom=dom, selectdom=domains, meanxpop=Xmeans, popnsize=Popn, B=100, method = "REML", data=data)', script)

    def test_generate_r_script_with_empty_vars(self):
        self.parent.of_interest_var = []
        self.parent.auxilary_vars = []
        self.parent.as_factor_var = []
        self.parent.index_var = []
        self.parent.aux_mean_vars = []
        self.parent.population_sample_size_var = []
        self.parent.domain_var = []
        self.parent.selection_method = "None"
        self.parent.method = "REML"
        self.parent.bootstrap = "50"
        script = generate_r_script(self.parent)
        self.assertIn('formula <- "" ~ 1', script)
    
    def test_generate_r_script_with_only_of_interest(self):
        self.parent.of_interest_var = ["y [Numeric]"]
        self.parent.auxilary_vars = []
        self.parent.as_factor_var = []
        self.parent.index_var = []
        self.parent.aux_mean_vars = []
        self.parent.population_sample_size_var = []
        self.parent.domain_var = []
        self.parent.selection_method = "None"
        self.parent.method = "REML"
        self.parent.bootstrap = "50"
        script = generate_r_script(self.parent)
        self.assertIn('formula <- y ~ 1', script)
    
    def test_generate_r_script_with_only_auxilary(self):
        self.parent.of_interest_var = []
        self.parent.auxilary_vars = ["x1 [Numeric]", "x2 [Numeric]"]
        self.parent.as_factor_var = []
        self.parent.index_var = []
        self.parent.aux_mean_vars = []
        self.parent.population_sample_size_var = []
        self.parent.domain_var = []
        self.parent.selection_method = "None"
        self.parent.method = "REML"
        self.parent.bootstrap = "50"
        script = generate_r_script(self.parent)
        self.assertIn('formula <- "" ~ x1 + x2', script)
    
    def test_generate_r_script_with_only_as_factor(self):
        self.parent.of_interest_var = []
        self.parent.auxilary_vars = []
        self.parent.as_factor_var = ["f1 [String]"]
        self.parent.index_var = []
        self.parent.aux_mean_vars = []
        self.parent.population_sample_size_var = []
        self.parent.domain_var = []
        self.parent.selection_method = "None"
        self.parent.method = "REML"
        self.parent.bootstrap = "50"
        script = generate_r_script(self.parent)
        self.assertIn('formula <- "" ~ as.factor(f1)', script)
    
    def test_generate_r_script_with_index(self):
        self.parent.of_interest_var = []
        self.parent.auxilary_vars = []
        self.parent.as_factor_var = []
        self.parent.index_var = ["idx [Numeric]"]
        self.parent.aux_mean_vars = []
        self.parent.population_sample_size_var = []
        self.parent.domain_var = []
        self.parent.selection_method = "None"
        self.parent.method = "REML"
        self.parent.bootstrap = "50"
        script = generate_r_script(self.parent)
        self.assertIn('Xmeans <- with(data, data.frame(idx,""))', script)
        self.assertIn('Popn <- with(data, data.frame(idx,""))', script)
    
    def test_generate_r_script_with_aux_mean(self):
        self.parent.of_interest_var = []
        self.parent.auxilary_vars = []
        self.parent.as_factor_var = []
        self.parent.index_var = []
        self.parent.aux_mean_vars = ["mx1 [Numeric]"]
        self.parent.population_sample_size_var = []
        self.parent.domain_var = []
        self.parent.selection_method = "None"
        self.parent.method = "REML"
        self.parent.bootstrap = "50"
        script = generate_r_script(self.parent)
        self.assertIn('Xmeans <- with(data, data.frame("",mx1)', script)
    
    def test_generate_r_script_with_aux_mean_and_index(self):
        self.parent.of_interest_var = []
        self.parent.auxilary_vars = []
        self.parent.as_factor_var = []
        self.parent.index_var = ["idx [Numeric]"]
        self.parent.aux_mean_vars = ["mx1 [Numeric]"]
        self.parent.population_sample_size_var = []
        self.parent.domain_var = []
        self.parent.selection_method = "None"
        self.parent.method = "REML"
        self.parent.bootstrap = "50"
        script = generate_r_script(self.parent)
        self.assertIn('Xmeans <- with(data, data.frame(idx,mx1)', script)
    
    def test_generate_r_script_with_population_sample_size(self):
        self.parent.of_interest_var = []
        self.parent.auxilary_vars = []
        self.parent.as_factor_var = []
        self.parent.index_var = []
        self.parent.aux_mean_vars = []
        self.parent.population_sample_size_var = ["pop [Numeric]"]
        self.parent.domain_var = []
        self.parent.selection_method = "None"
        self.parent.method = "REML"
        self.parent.bootstrap = "50"
        script = generate_r_script(self.parent)
        self.assertIn('Popn <- with(data, data.frame("",pop))', script)
    
    def test_generate_r_script_with_domain(self):
        self.parent.of_interest_var = []
        self.parent.auxilary_vars = []
        self.parent.as_factor_var = []
        self.parent.index_var = []
        self.parent.aux_mean_vars = []
        self.parent.population_sample_size_var = []
        self.parent.domain_var = ["dom [Numeric]"]
        self.parent.selection_method = "None"
        self.parent.method = "REML"
        self.parent.bootstrap = "50"
        script = generate_r_script(self.parent)
        self.assertIn('domains=Xmeans[,1]', script)
    
    def test_generate_r_script_with_multi_auxilary_and_mean_aux(self):
        self.parent.of_interest_var = ["y [Numeric]"]
        self.parent.auxilary_vars = ["x1 [Numeric]", "x2 [Numeric]"]
        self.parent.as_factor_var = []
        self.parent.index_var = []
        self.parent.aux_mean_vars = ["mx1 [Numeric]", "mx2 [Numeric]"]
        self.parent.population_sample_size_var = []
        self.parent.domain_var = []
        self.parent.selection_method = "None"
        self.parent.method = "REML"
        self.parent.bootstrap = "50"
        script = generate_r_script(self.parent)
        self.assertIn('formula <- y ~ x1 + x2', script)
    
    def test_generate_r_script_with_multi_of_interest(self):
        self.parent.of_interest_var = ["y1 [Numeric]", "y2 [Numeric]"]
        self.parent.auxilary_vars = []
        self.parent.as_factor_var = []
        self.parent.index_var = []
        self.parent.aux_mean_vars = []
        self.parent.population_sample_size_var = []
        self.parent.domain_var = []
        self.parent.selection_method = "None"
        self.parent.method = "REML"
        self.parent.bootstrap = "50"
        script = generate_r_script(self.parent)
        self.assertIn('formula <- y1 ~ 1', script)
    
    def test_generate_r_script_with_multi_auxilary_and_as_factor(self):
        self.parent.of_interest_var = ["y [Numeric]"]
        self.parent.auxilary_vars = ["x1 [Numeric]", "x2 [Numeric]"]
        self.parent.as_factor_var = ["f1 [String]", "f2 [String]"]
        self.parent.index_var = []
        self.parent.aux_mean_vars = []
        self.parent.population_sample_size_var = []
        self.parent.domain_var = []
        self.parent.selection_method = "None"
        self.parent.method = "REML"
        self.parent.bootstrap = "50"
        script = generate_r_script(self.parent)
        self.assertIn('formula <- y ~ x1 + x2 + as.factor(f1) + as.factor(f2)', script)
    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    unittest.main()
        