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
                show_r_script(parent)
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
        show_r_script(parent)

def assign_vardir(parent):
    selected_indexes = parent.variables_list.selectedIndexes()
    if selected_indexes:
        all_string = True
        for index in selected_indexes:
            type_of_var = index.data().split(" [")[1].replace("]", "")
            if type_of_var != "String":
                all_string = False
                parent.vardir_var = [index.data()]
                parent.vardir_model.setStringList(parent.vardir_var)
                parent.variables_list.model().removeRow(selected_indexes[-1].row())  # Remove from variables list
                show_r_script(parent)
                break
        if all_string:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText("All selected variables are of type String. Vardir variable must be of type Numeric.")
            msg.setWindowTitle("Warning")
            msg.exec()

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
    def remove_selected_items(selected_list, target_list, model):
        selected_items = [index.data() for index in selected_list.selectedIndexes()]
        if selected_items:
            for item in selected_items:
                if item in target_list:
                    target_list.remove(item)
                parent.variables_list.model().insertRow(0)  # Add back to variables list
                parent.variables_list.model().setData(parent.variables_list.model().index(0), item)
            model.setStringList(target_list)  # Update the model
            show_r_script(parent)

    remove_selected_items(parent.of_interest_list, parent.of_interest_var, parent.of_interest_model)
    remove_selected_items(parent.auxilary_list, parent.auxilary_vars, parent.auxilary_model)
    remove_selected_items(parent.vardir_list, parent.vardir_var, parent.vardir_model)
    remove_selected_items(parent.as_factor_list, parent.as_factor_var, parent.as_factor_model)
    remove_selected_items(parent.domain_list, parent.domain_var, parent.domain_model)

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
    if parent.selection_method=="Stepwise":
        parent.selection_method = "both"
    if parent.selection_method and parent.selection_method != "None" and auxilary_vars:
        r_script += f'stepwise_model <- step(formula, direction="{parent.selection_method.lower()}")\n'
        r_script += f'final_formula <- formula(stepwise_model)\n'
        r_script += f'model<-{parent.model_method} (final_formula, iter.update={parent.iter_update}, iter.mcmc = {parent.iter_mcmc}, burn.in ={parent.burn_in} , data=data)'
    else:
        r_script += f'model<-{parent.model_method} (formula, iter.update={parent.iter_update}, iter.mcmc = {parent.iter_mcmc}, burn.in ={parent.burn_in}, data=data)'
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

    method_label = QLabel("Stepwise Selection Method:")
    # layout.addWidget(method_label)

    # parent.method_combo = QComboBox()
    # parent.method_combo.addItems(["None", "Stepwise", "Forward", "Backward"])
    # layout.addWidget(parent.method_combo)

    iter_update_label = QLabel("Number of Iteration Update (minimum 2):")
    layout.addWidget(iter_update_label)
    
    parent.iter_update = QLineEdit()
    parent.iter_update.setValidator(QIntValidator())
    parent.iter_update.setText("3")  # Set default value to 3
    layout.addWidget(parent.iter_update)
    
    iter_mcmc_label = QLabel("Number of Total Iterations per Chain:")
    layout.addWidget(iter_mcmc_label)
    
    parent.iter_mcmc = QLineEdit()
    parent.iter_mcmc.setValidator(QIntValidator())
    parent.iter_mcmc.setText("2000")  # Set default value to 2000
    layout.addWidget(parent.iter_mcmc)
    
    burn_in_label = QLabel("Number of iterations to discard at the beginning:")
    layout.addWidget(burn_in_label)
    
    parent.burn_in = QLineEdit()
    parent.burn_in.setValidator(QIntValidator())
    parent.burn_in.setText("1000")  # Set default value to 1000
    layout.addWidget(parent.burn_in)
    

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
    parent.iter_update = parent.iter_update.text()
    parent.iter_mcmc = parent.iter_mcmc.text()
    parent.burn_in = parent.burn_in.text()
    dialog.accept()
    show_r_script(parent)
    
import unittest
from unittest.mock import MagicMock
from PyQt6.QtWidgets import QApplication
import sys

class TestSaeHBArea(unittest.TestCase):

    def setUp(self):
        self.parent = MagicMock()
        self.parent.of_interest_var = ["var1 [Numeric]"]
        self.parent.auxilary_vars = ["var2 [Numeric]", "var3 [Numeric]"]
        self.parent.vardir_var = ["var4 [Numeric]"]
        self.parent.as_factor_var = ["var5 [String]"]

        self.parent.of_interest_model = MagicMock()
        self.parent.auxilary_model = MagicMock()
        self.parent.vardir_model = MagicMock()
        self.parent.as_factor_model = MagicMock()
        self.parent.variables_list = MagicMock()
        self.parent.of_interest_list = MagicMock()
        self.parent.auxilary_list = MagicMock()
        self.parent.vardir_list = MagicMock()
        self.parent.as_factor_list = MagicMock()

    def test_unassign_variable_of_interest(self):
        self.parent.of_interest_list.selectedIndexes.return_value = [MagicMock(data=MagicMock(return_value="var1 [Numeric]"))]
        unassign_variable(self.parent)
        self.assertEqual(self.parent.of_interest_var, [])
        self.parent.of_interest_model.setStringList.assert_called_with([])
        self.parent.variables_list.model().insertRow.assert_called_with(0)
        self.parent.variables_list.model().setData.assert_called_with(self.parent.variables_list.model().index(0), "var1 [Numeric]")

    def test_unassign_variable_auxilary(self):
        self.parent.auxilary_list.selectedIndexes.return_value = [MagicMock(data=MagicMock(return_value="var2 [Numeric]"))]
        unassign_variable(self.parent)
        self.assertEqual(self.parent.auxilary_vars, ["var3 [Numeric]"])
        self.parent.auxilary_model.setStringList.assert_called_with(["var3 [Numeric]"])
        self.parent.variables_list.model().insertRow.assert_called_with(0)
        self.parent.variables_list.model().setData.assert_called_with(self.parent.variables_list.model().index(0), "var2 [Numeric]")

    def test_unassign_variable_vardir(self):
        self.parent.vardir_list.selectedIndexes.return_value = [MagicMock(data=MagicMock(return_value="var4 [Numeric]"))]
        unassign_variable(self.parent)
        self.assertEqual(self.parent.vardir_var, [])
        self.parent.vardir_model.setStringList.assert_called_with([])
        self.parent.variables_list.model().insertRow.assert_called_with(0)
        self.parent.variables_list.model().setData.assert_called_with(self.parent.variables_list.model().index(0), "var4 [Numeric]")

    def test_unassign_variable_as_factor(self):
        self.parent.as_factor_list.selectedIndexes.return_value = [MagicMock(data=MagicMock(return_value="var5 [String]"))]
        unassign_variable(self.parent)
        self.assertEqual(self.parent.as_factor_var, [])
        self.parent.as_factor_model.setStringList.assert_called_with([])
        self.parent.variables_list.model().insertRow.assert_called_with(0)
        self.parent.variables_list.model().setData.assert_called_with(self.parent.variables_list.model().index(0), "var5 [String]")
        
    def test_assign_of_interest_with_numeric(self):
        index = MagicMock()
        index.data.return_value = "variable1 [Numeric]"
        self.parent.variables_list.selectedIndexes.return_value = [index]

        assign_of_interest(self.parent)

        self.assertEqual(self.parent.of_interest_var, ["variable1 [Numeric]"])
        self.parent.of_interest_model.setStringList.assert_called_with(["variable1 [Numeric]"])
        self.parent.variables_list.model().removeRow.assert_called_once()
    
    def test_assign_aux_mean_with_string(self):
        index = MagicMock()
        index.data.return_value = "variable1 [String]"
        self.parent.variables_list.selectedIndexes.return_value = [index]
        self.parent.auxilary_vars = []
        with unittest.mock.patch("PyQt6.QtWidgets.QMessageBox.exec") as mock_exec:
            assign_auxilary(self.parent)
            self.assertEqual(self.parent.auxilary_vars, [])
            self.parent.variables_list.model().removeRow.assert_not_called()
            mock_exec.assert_called_once()
    
    def test_assign_vardir_with_numeric(self):
        index = MagicMock()
        index.data.return_value = "variable1 [Numeric]"
        self.parent.variables_list.selectedIndexes.return_value = [index]

        assign_vardir(self.parent)

        self.assertEqual(self.parent.vardir_var, ["variable1 [Numeric]"])
        self.parent.vardir_model.setStringList.assert_called_with(["variable1 [Numeric]"])
        self.parent.variables_list.model().removeRow.assert_called_once()
    
    def test_assign_as_factor(self):
        self.parent.as_factor_var = []
        index1 = MagicMock()
        index1.data.return_value = "variable1 [String]"
        self.parent.variables_list.selectedIndexes.return_value = [index1]

        assign_as_factor(self.parent)

        self.assertEqual(self.parent.as_factor_var, ["variable1 [String]"])
        self.parent.as_factor_model.setStringList.assert_called_with(["variable1 [String]"])
        self.parent.variables_list.model().removeRow.assert_any_call(index1.row())
    
    def test_generate_r_script(self):
        self.parent.of_interest_var = ["var1 [Numeric]"]
        self.parent.auxilary_vars = ["var2 [Numeric]", "var3 [Numeric]"]
        self.parent.vardir_var = ["var4 [Numeric]"]
        self.parent.as_factor_var = ["var5 [String]"]
        self.parent.selection_method = "Stepwise"
        self.parent.model_method = "lm"
        self.parent.iter_update = "3"
        self.parent.iter_mcmc = "2000"
        self.parent.burn_in = "1000"

        r_script = generate_r_script(self.parent)
        
        expected_script = (
            'names(data) <- gsub(" ", "_", names(data)); #Replace space with underscore\n'
            'formula <- var1 ~ var2 + var3 + as.factor(var5)\n'
            'stepwise_model <- step(formula, direction="both")\n'
            'final_formula <- formula(stepwise_model)\n'
            'model<-lm (final_formula, iter.update=3, iter.mcmc = 2000, burn.in =1000 , data=data)'
        )
        
        self.assertEqual(r_script.strip(), expected_script.strip())
    
    def test_generate_r_script_with_empty_vars(self):
        self.parent.of_interest_var = []
        self.parent.auxilary_vars = []
        self.parent.vardir_var = []
        self.parent.as_factor_var = []
        self.parent.selection_method = "Stepwise"
        self.parent.model_method = "lm"
        self.parent.iter_update = "3"
        self.parent.iter_mcmc = "2000"
        self.parent.burn_in = "1000"

        r_script = generate_r_script(self.parent)
        
        expected_script = (
            'names(data) <- gsub(" ", "_", names(data)); #Replace space with underscore\n'
            'formula <- "" ~ 1\n'
            'stepwise_model <- step(formula, direction="both")\n'
            'final_formula <- formula(stepwise_model)\n'
            'model<-lm (final_formula, iter.update=3, iter.mcmc = 2000, burn.in =1000 , data=data)'
        )
        
        self.assertEqual(r_script.strip(), expected_script.strip())
    
    def test_generate_r_script_with_only_as_factor(self):
        self.parent.of_interest_var = []
        self.parent.auxilary_vars = []
        self.parent.vardir_var = []
        self.parent.as_factor_var = ["var5 [String]"]
        self.parent.selection_method = "Stepwise"
        self.parent.model_method = "lm"
        self.parent.iter_update = "3"
        self.parent.iter_mcmc = "2000"
        self.parent.burn_in = "1000"

        r_script = generate_r_script(self.parent)
        
        expected_script = (
            'names(data) <- gsub(" ", "_", names(data)); #Replace space with underscore\n'
            'formula <- "" ~ as.factor(var5)\n'
            'stepwise_model <- step(formula, direction="both")\n'
            'final_formula <- formula(stepwise_model)\n'
            'model<-lm (final_formula, iter.update=3, iter.mcmc = 2000, burn.in =1000 , data=data)'
        )
        
        self.assertEqual(r_script.strip(), expected_script.strip())
    
    def test_generate_r_script_with_only_auxilary(self):
        self.parent.of_interest_var = []
        self.parent.auxilary_vars = ["var2 [Numeric]", "var3 [Numeric]"]
        self.parent.vardir_var = []
        self.parent.as_factor_var = []
        self.parent.selection_method = "Stepwise"
        self.parent.model_method = "lm"
        self.parent.iter_update = "3"
        self.parent.iter_mcmc = "2000"
        self.parent.burn_in = "1000"

        r_script = generate_r_script(self.parent)
        
        expected_script = (
            'names(data) <- gsub(" ", "_", names(data)); #Replace space with underscore\n'
            'formula <- "" ~ var2 + var3\n'
            'stepwise_model <- step(formula, direction="both")\n'
            'final_formula <- formula(stepwise_model)\n'
            'model<-lm (final_formula, iter.update=3, iter.mcmc = 2000, burn.in =1000 , data=data)'
        )
        
        self.assertEqual(r_script.strip(), expected_script.strip())
    
    def test_generate_r_script_with_only_vardir(self):
        self.parent.of_interest_var = []
        self.parent.auxilary_vars = []
        self.parent.vardir_var = ["var4 [Numeric]"]
        self.parent.as_factor_var = []
        self.parent.selection_method = "Stepwise"
        self.parent.model_method = "lm"
        self.parent.iter_update = "3"
        self.parent.iter_mcmc = "2000"
        self.parent.burn_in = "1000"

        r_script = generate_r_script(self.parent)
        
        expected_script = (
            'names(data) <- gsub(" ", "_", names(data)); #Replace space with underscore\n'
            'formula <- "" ~ 1\n'
            'stepwise_model <- step(formula, direction="both")\n'
            'final_formula <- formula(stepwise_model)\n'
            'model<-lm (final_formula, iter.update=3, iter.mcmc = 2000, burn.in =1000 , data=data)'
        )
        
        self.assertEqual(r_script.strip(), expected_script.strip())
        
    def test_generate_r_script_with_empty_selection_method(self):
        self.parent.of_interest_var = ["var1 [Numeric]"]
        self.parent.auxilary_vars = ["var2 [Numeric]", "var3 [Numeric]"]
        self.parent.vardir_var = ["var4 [Numeric]"]
        self.parent.as_factor_var = ["var5 [String]"]
        self.parent.selection_method = ""
        self.parent.model_method = "lm"
        self.parent.iter_update = "3"
        self.parent.iter_mcmc = "2000"
        self.parent.burn_in = "1000"

        r_script = generate_r_script(self.parent)
        
        expected_script = (
            'names(data) <- gsub(" ", "_", names(data)); #Replace space with underscore\n'
            'formula <- var1 ~ var2 + var3 + as.factor(var5)\n'
            'model<-lm (formula, iter.update=3, iter.mcmc = 2000, burn.in =1000, data=data)'
        )
        
        self.assertEqual(r_script.strip(), expected_script.strip())
        
    def test_generate_r_script_with_only_of_interest(self):
        self.parent.of_interest_var = ["var1 [Numeric]"]
        self.parent.auxilary_vars = []
        self.parent.vardir_var = []
        self.parent.as_factor_var = []
        self.parent.selection_method = "Stepwise"
        self.parent.model_method = "lm"
        self.parent.iter_update = "3"
        self.parent.iter_mcmc = "2000"
        self.parent.burn_in = "1000"

        r_script = generate_r_script(self.parent)
        
        expected_script = (
            'names(data) <- gsub(" ", "_", names(data)); #Replace space with underscore\n'
            'formula <- var1 ~ 1\n'
            'stepwise_model <- step(formula, direction="both")\n'
            'final_formula <- formula(stepwise_model)\n'
            'model<-lm (final_formula, iter.update=3, iter.mcmc = 2000, burn.in =1000 , data=data)'
        )
        
        self.assertEqual(r_script.strip(), expected_script.strip())
        
    def test_generate_r_script_with_empty_of_interest(self):
        self.parent.of_interest_var = []
        self.parent.auxilary_vars = ["var2 [Numeric]", "var3 [Numeric]"]
        self.parent.vardir_var = ["var4 [Numeric]"]
        self.parent.as_factor_var = ["var5 [String]"]
        self.parent.selection_method = "Stepwise"
        self.parent.model_method = "lm"
        self.parent.iter_update = "3"
        self.parent.iter_mcmc = "2000"
        self.parent.burn_in = "1000"

        r_script = generate_r_script(self.parent)
        
        expected_script = (
            'names(data) <- gsub(" ", "_", names(data)); #Replace space with underscore\n'
            'formula <- "" ~ var2 + var3 + as.factor(var5)\n'
            'stepwise_model <- step(formula, direction="both")\n'
            'final_formula <- formula(stepwise_model)\n'
            'model<-lm (final_formula, iter.update=3, iter.mcmc = 2000, burn.in =1000 , data=data)'
        )
        
        self.assertEqual(r_script.strip(), expected_script.strip())
    
    def test_generate_r_scrip_with_multiple_as_factor(self):
        self.parent.of_interest_var = ["var1 [Numeric]"]
        self.parent.auxilary_vars = ["var2 [Numeric]", "var3 [Numeric]"]
        self.parent.vardir_var = []
        self.parent.as_factor_var = ["var4 [String]", "var5 [String]"]
        self.parent.selection_method = "Stepwise"
        self.parent.model_method = "lm"
        self.parent.iter_update = "3"
        self.parent.iter_mcmc = "2000"
        self.parent.burn_in = "1000"

        r_script = generate_r_script(self.parent)
        
        expected_script = (
            'names(data) <- gsub(" ", "_", names(data)); #Replace space with underscore\n'
            'formula <- var1 ~ var2 + var3 + as.factor(var4) + as.factor(var5)\n'
            'stepwise_model <- step(formula, direction="both")\n'
            'final_formula <- formula(stepwise_model)\n'
            'model<-lm (final_formula, iter.update=3, iter.mcmc = 2000, burn.in =1000 , data=data)'
        )
        
        self.assertEqual(r_script.strip(), expected_script.strip())
    
    def test_generate_r_script_with_empty_as_factor(self):
        self.parent.of_interest_var = ["var1 [Numeric]"]
        self.parent.auxilary_vars = ["var2 [Numeric]", "var3 [Numeric]"]
        self.parent.vardir_var = []
        self.parent.as_factor_var = []
        self.parent.selection_method = "Stepwise"
        self.parent.model_method = "lm"
        self.parent.iter_update = "3"
        self.parent.iter_mcmc = "2000"
        self.parent.burn_in = "1000"

        r_script = generate_r_script(self.parent)
        
        expected_script = (
            'names(data) <- gsub(" ", "_", names(data)); #Replace space with underscore\n'
            'formula <- var1 ~ var2 + var3\n'
            'stepwise_model <- step(formula, direction="both")\n'
            'final_formula <- formula(stepwise_model)\n'
            'model<-lm (final_formula, iter.update=3, iter.mcmc = 2000, burn.in =1000 , data=data)'
        )
        
        self.assertEqual(r_script.strip(), expected_script.strip())
    
    def test_generate_r_script_with_empty_auxilary(self):
        self.parent.of_interest_var = ["var1 [Numeric]"]
        self.parent.auxilary_vars = []
        self.parent.vardir_var = ["var4 [Numeric]"]
        self.parent.as_factor_var = ["var5 [String]"]
        self.parent.selection_method = "Stepwise"
        self.parent.model_method = "lm"
        self.parent.iter_update = "3"
        self.parent.iter_mcmc = "2000"
        self.parent.burn_in = "1000"

        r_script = generate_r_script(self.parent)
        
        expected_script = (
            'names(data) <- gsub(" ", "_", names(data)); #Replace space with underscore\n'
            'formula <- var1 ~ as.factor(var5)\n'
            'stepwise_model <- step(formula, direction="both")\n'
            'final_formula <- formula(stepwise_model)\n'
            'model<-lm (final_formula, iter.update=3, iter.mcmc = 2000, burn.in =1000 , data=data)'
        )
        
        self.assertEqual(r_script.strip(), expected_script.strip())
    
    def test_generate_r_script_with_empty_vardir(self):
        self.parent.of_interest_var = ["var1 [Numeric]"]
        self.parent.auxilary_vars = ["var2 [Numeric]", "var3 [Numeric]"]
        self.parent.vardir_var = []
        self.parent.as_factor_var = ["var5 [String]"]
        self.parent.selection_method = "Stepwise"
        self.parent.model_method = "lm"
        self.parent.iter_update = "3"
        self.parent.iter_mcmc = "2000"
        self.parent.burn_in = "1000"

        r_script = generate_r_script(self.parent)
        
        expected_script = (
            'names(data) <- gsub(" ", "_", names(data)); #Replace space with underscore\n'
            'formula <- var1 ~ var2 + var3 + as.factor(var5)\n'
            'stepwise_model <- step(formula, direction="both")\n'
            'final_formula <- formula(stepwise_model)\n'
            'model<-lm (final_formula, iter.update=3, iter.mcmc = 2000, burn.in =1000 , data=data)'
        )
        
        self.assertEqual(r_script.strip(), expected_script.strip())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    unittest.main()