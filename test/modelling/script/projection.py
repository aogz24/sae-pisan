from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QAbstractItemView, QTextEdit, QComboBox, QLineEdit
from PyQt6.QtGui import QDoubleValidator, QIntValidator
from PyQt6.QtWidgets import QMessageBox

def assign_of_interest(parent):
    selected_indexes = parent.variables_list.selectedIndexes()
    if selected_indexes:
        all_string = False
        for index in selected_indexes:
            type_of_var = index.data().split(" [")[1].replace("]", "")
            if type_of_var == "String" and parent.projection_method == "Linear":
                all_string = True
                break
            else:
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

def assign_index(parent):
    selected_indexes = parent.variables_list.selectedIndexes()
    if selected_indexes:
        for index in selected_indexes:
            parent.index_var = [index.data()]
            parent.index_model.setStringList(parent.index_var)
            parent.variables_list.model().removeRow(selected_indexes[-1].row())  # Remove from variables list
            show_r_script(parent)
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
        show_r_script(parent)
        
def assign_domains(parent):
    selected_indexes = parent.variables_list.selectedIndexes()
    if selected_indexes:
        parent.domain_var = [selected_indexes[0].data()]  # Only one variable
        parent.domain_model.setStringList(parent.domain_var)
        parent.variables_list.model().removeRow(selected_indexes[0].row())  # Remove from variables list
        show_r_script(parent)
        
def assign_weight(parent):
    selected_indexes = parent.variables_list.selectedIndexes()
    if selected_indexes:
        all_string = True
        for index in selected_indexes:
            type_of_var = index.data().split(" [")[1].replace("]", "")
            if type_of_var != "String":
                all_string = False
                parent.weight_var = [index.data()]  # Only one variable
                parent.weight_model.setStringList(parent.weight_var)
                parent.variables_list.model().removeRow(index.row())  # Remove from variables list
                show_r_script(parent)
                break
        if all_string:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText("All selected variables are of type String. Weight variable must be of type Numeric.")
            msg.setWindowTitle("Warning")
            msg.exec()

def assign_strata(parent):
    selected_indexes = parent.variables_list.selectedIndexes()
    if selected_indexes:
        parent.strata_var = [selected_indexes[0].data()]  # Only one variable
        parent.strata_model.setStringList(parent.strata_var)
        parent.variables_list.model().removeRow(selected_indexes[0].row())  # Remove from variables list
        show_r_script(parent)

def unassign_variable(parent):
    selected_indexes = parent.of_interest_list.selectedIndexes()
    if selected_indexes:
        selected_items = [index.data() for index in selected_indexes]
        parent.of_interest_var = [var for var in parent.of_interest_var if var not in selected_items]
        parent.of_interest_model.setStringList(parent.of_interest_var)
        for item in selected_items:
            parent.variables_list.model().insertRow(0)  # Add back to variables list
            parent.variables_list.model().setData(parent.variables_list.model().index(0), item)
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

    selected_indexes = parent.index_list.selectedIndexes()
    if selected_indexes:
        selected_items = [index.data() for index in selected_indexes]
        parent.index_var = [var for var in parent.index_var if var not in selected_items]
        parent.index_model.setStringList(parent.index_var)
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
        return

    selected_indexes = parent.domain_list.selectedIndexes()
    if selected_indexes:
        selected_items = [index.data() for index in selected_indexes]
        parent.domain_var = [var for var in parent.domain_var if var not in selected_items]
        parent.domain_model.setStringList(parent.domain_var)
        for item in selected_items:
            parent.variables_list.model().insertRow(0)  # Add back to variables list
            parent.variables_list.model().setData(parent.variables_list.model().index(0), item)
        show_r_script(parent)
        return
    
    selected_indexes = parent.strata_list.selectedIndexes()
    if selected_indexes:
        selected_items = [index.data() for index in selected_indexes]
        parent.strata_var = [var for var in parent.strata_var if var not in selected_items]
        parent.strata_model.setStringList(parent.strata_var)
        for item in selected_items:
            parent.variables_list.model().insertRow(0)  # Add back to variables list
            parent.variables_list.model().setData(parent.variables_list.model().index(0), item)
        show_r_script(parent)
        return

    selected_indexes = parent.weight_list.selectedIndexes()
    if selected_indexes:
        selected_items = [index.data() for index in selected_indexes]
        parent.weight_var = [var for var in parent.weight_var if var not in selected_items]
        parent.weight_model.setStringList(parent.weight_var)
        for item in selected_items:
            parent.variables_list.model().insertRow(0)  # Add back to variables list
            parent.variables_list.model().setData(parent.variables_list.model().index(0), item)
        show_r_script(parent)
        return

def get_selected_variables(parent):
    return parent.of_interest_var, parent.auxilary_vars, parent.vardir_var, parent.as_factor_var

def process_vars(vars_list, prefix, suffix):
    for var in vars_list:
        var_name = var.split(" [")[0].replace(" ", "_")
        var_name_edit = f"{prefix}{var_name}{suffix}"
        r_script += f'{var_name} <- data["{var_name_edit}"];\n'

def generate_r_script(parent):
    def format_var(var_list, as_factor=False):
        if not var_list:
            return ''
        if as_factor:
            return " + ".join([f'{var.split(" [")[0].replace(" ", "_")}' for var in var_list])
        return " + ".join([var.split(" [")[0].replace(" ", "_") for var in var_list])

    def format_single_var(var):
        return f'{var[0].split(" [")[0].replace(" ", "_")}' if var else ''

    def format_edit_var(var, prefix):
        return f'{prefix}{var.split(" [")[0].replace(" ", "_")}'
    
    def format_edit_var_before(var, prefix):
        return f'{var.split(" [")[0].replace(" ", "_")}{prefix}'

    of_interest_var = format_single_var(parent.of_interest_var)
    auxilary_vars = format_var(parent.auxilary_vars)
    as_factor_var = format_var(parent.as_factor_var, as_factor=True)
    index_var = format_single_var(parent.index_var)
    domain_var = format_single_var(parent.domain_var)
    weight = format_single_var(parent.weight_var)
    strata = format_single_var(parent.strata_var) if parent.strata_var else 'NULL'

    model_var = {
        "Linear": "linear_reg()",
        "Logistic": "logistic_reg()",
        "SVM Linear": "svm_linear(mode='classification')",
        "SVM RBF": "svm_rbf(mode='classification')",
        "Neural Network": f"mlp(mode='classification', engine='nnet', epochs={parent.epoch}, hidden_units={parent.hidden_unit}, learn_rate={parent.learning_rate})"
    }.get(parent.projection_method, 'gb_model')

    if auxilary_vars or as_factor_var:
        formula_parts = [of_interest_var]
        if auxilary_vars:
            formula_parts.append(auxilary_vars)
        if as_factor_var:
            formula_parts.append(as_factor_var)
        formula = f"{of_interest_var} ~ {' + '.join(filter(None, formula_parts[1:]))}"
    else:
        formula = f"{of_interest_var} ~ 1"
    
    r_script = f'formula <- {formula}\n'
    if parent.projection_method=="Gradient Boost":
        r_script += f'show_engines("boost_tree")\n'
        r_script += f'gb_model <- boost_tree( mtry = tune(), trees = tune(), min_n = tune(), tree_depth = tune(), learn_rate = tune(), engine = "xgboost")\n'

    if parent.var_position == "After":
        if parent.of_interest_var:
            var = parent.of_interest_var[0]
            var_name_edit = format_edit_var(var, parent.model_name + parent.separator)
            if parent.projection_method != "Linear":
                r_script += f'{var.split(" [")[0].replace(" ", "_")} <- as.factor(data[["{var_name_edit}"]]);\n'
            else:
                r_script += f'{var.split(" [")[0].replace(" ", "_")} <- data[["{var_name_edit}"]];\n'
        
        for var in parent.auxilary_vars:
            var_name_edit = format_edit_var(var, parent.model_name + parent.separator)
            r_script += f'{var.split(" [")[0].replace(" ", "_")} <- data[["{var_name_edit}"]];\n'
        
        for var in parent.as_factor_var:
            var_name_edit = format_edit_var(var, parent.model_name + parent.separator)
            r_script += f'{var.split(" [")[0].replace(" ", "_")} <- as.factor(data[["{var_name_edit}"]]);\n'
            
        for var, prefix in [(domain_var, parent.model_name), (weight, parent.model_name), (strata, parent.model_name), (index_var, parent.model_name)]:
            if var and var != 'NULL':
                var_edit = format_edit_var(var, prefix + parent.separator)
                r_script += f'{var} <- data[["{var_edit}"]];\n'
                
        all_vars = parent.auxilary_vars + parent.as_factor_var + parent.of_interest_var + parent.domain_var + parent.index_var + parent.strata_var+parent.weight_var
        r_script += f'data_model <- data.frame({", ".join([var.split(" [")[0].replace(" ", "_") for var in all_vars])});\n'
        r_script += f'colnames(data_model) <- sub("^{prefix}\\\\{parent.separator}", "", colnames(data_model))\n'
        
        if parent.of_interest_var:
            var = parent.of_interest_var[0]
            var_name_edit = format_edit_var(var, parent.projection_name + parent.separator)
            if parent.projection_method != "Linear":
                r_script += f'{var.split(" [")[0].replace(" ", "_")} <- as.factor(data[["{var_name_edit}"]]);\n'
            else:
                r_script += f'{var.split(" [")[0].replace(" ", "_")} <- data[["{var_name_edit}"]];\n'
        
        for var in parent.auxilary_vars:
            var_name_edit = format_edit_var(var, parent.projection_name + parent.separator)
            r_script += f'{var.split(" [")[0].replace(" ", "_")} <- data[["{var_name_edit}"]];\n'
        
        for var in parent.as_factor_var:
            var_name_edit = format_edit_var(var, parent.projection_name + parent.separator)
            r_script += f'{var.split(" [")[0].replace(" ", "_")} <- as.factor(data[["{var_name_edit}"]]);\n'

        for var, prefix in [(domain_var, parent.projection_name), (weight, parent.projection_name), (strata, parent.projection_name), (index_var, parent.projection_name)]:
            if var and var != 'NULL':
                var_edit = format_edit_var(var, prefix + parent.separator)
                r_script += f'{var} <- data[["{var_edit}"]];\n'

        all_vars = parent.auxilary_vars + parent.as_factor_var + parent.of_interest_var + parent.domain_var + parent.index_var + parent.strata_var+parent.weight_var
        r_script += f'data_proj <- data.frame({", ".join([var.split(" [")[0].replace(" ", "_") for var in all_vars])});\n'
        if(parent.projection_method != "Linear"):
            r_script += f'data_model${of_interest_var} <- as.factor(data_model${of_interest_var})\n'
            r_script += f'data_proj${of_interest_var} <- as.factor(data_proj${of_interest_var})\n'
        r_script += f'colnames(data_proj) <- colnames(data_model)\n'
    
    if parent.var_position == "Before":
        if parent.of_interest_var:
            var = parent.of_interest_var[0]
            var_name_edit = format_edit_var_before(var, parent.separator + parent.model_name)
            if parent.projection_method != "Linear":
                r_script += f'{var.split(" [")[0].replace(" ", "_")} <- as.factor(data[["{var_name_edit}"]]);\n'
            else:
                r_script += f'{var.split(" [")[0].replace(" ", "_")} <- data[["{var_name_edit}"]];\n'
        
        for var in parent.auxilary_vars:
            var_name_edit = format_edit_var_before(var, parent.separator + parent.model_name)
            r_script += f'{var.split(" [")[0].replace(" ", "_")} <- data[["{var_name_edit}"]];\n'
        
        for var in parent.as_factor_var:
            var_name_edit = format_edit_var_before(var, parent.separator + parent.model_name)
            r_script += f'{var.split(" [")[0].replace(" ", "_")} <- as.factor(data[["{var_name_edit}"]]);\n'

        for var, prefix in [(domain_var, parent.model_name), (weight, parent.model_name), (strata, parent.model_name), (index_var, parent.model_name)]:
            if var and var != 'NULL':
                var_edit = format_edit_var_before(var, parent.separator + prefix)
                r_script += f'{var} <- data[["{var_edit}"]];\n'
                
        all_vars = parent.auxilary_vars + parent.as_factor_var + parent.of_interest_var + parent.domain_var + parent.index_var + parent.strata_var+parent.weight_var
        r_script += f'data_model <- data.frame({", ".join([var.split(" [")[0].replace(" ", "_") for var in all_vars])});\n'
        r_script += f'colnames(data_model) <- sub("\\\\{parent.separator}{prefix}$", "", colnames(data_model))\n'
        
        if parent.of_interest_var:
            var = parent.of_interest_var[0]
            var_name_edit = format_edit_var_before(var, parent.separator + parent.projection_name)
            if parent.projection_method != "Linear":
                r_script += f'{var.split(" [")[0].replace(" ", "_")} <- as.factor(data[["{var_name_edit}"]]);\n'
            else:
                r_script += f'{var.split(" [")[0].replace(" ", "_")} <- data[["{var_name_edit}"]];\n'
        
        for var in parent.auxilary_vars:
            var_name_edit = format_edit_var_before(var, parent.separator + parent.projection_name)
            r_script += f'{var.split(" [")[0].replace(" ", "_")} <- data[["{var_name_edit}"]];\n'
        
        for var in parent.as_factor_var:
            var_name_edit = format_edit_var_before(var, parent.separator + parent.projection_name)
            r_script += f'{var.split(" [")[0].replace(" ", "_")} <- as.factor(data[["{var_name_edit}"]]);\n'
            
        for var, prefix in [(domain_var, parent.projection_name), (weight, parent.projection_name), (strata, parent.projection_name), (index_var, parent.projection_name)]:
            if var and var != 'NULL':
                var_edit = format_edit_var_before(var, parent.separator + prefix)
                r_script += f'{var} <- data[["{var_edit}"]];\n'
        
        all_vars = parent.auxilary_vars + parent.as_factor_var + parent.of_interest_var + parent.domain_var + parent.index_var + parent.strata_var+parent.weight_var
        r_script += f'data_proj <- data.frame({", ".join([var.split(" [")[0].replace(" ", "_") for var in all_vars])});\n'
        if(parent.projection_method != "Linear"):
            r_script += f'data_model${of_interest_var} <- as.factor(data_model${of_interest_var})\n'
            r_script += f'data_proj${of_interest_var} <- as.factor(data_proj${of_interest_var})\n'
        r_script += f'colnames(data_proj) <- colnames(data_model)\n'
    
    r_script += f'data_model <- data_model %>% filter(!is.na({of_interest_var}))\n'
    r_script += f'data_proj <- data_proj %>% filter(!is.na({of_interest_var}))\n'
    r_script += f'data_model <- data_model %>% filter(!is.null({of_interest_var}))\n'
    r_script += f'data_proj <- data_proj %>% filter(!is.null({of_interest_var}))\n'
    
    
    if parent.selection_method == "Stepwise":
        parent.selection_method = "both"
    if parent.selection_method and parent.selection_method != "None" and auxilary_vars:
        r_script += f'stepwise_model <- step(formula, direction="{parent.selection_method.lower()}")\n'
        r_script += f'final_formula <- formula(stepwise_model)\n'
        r_script += f'model <- projection(final_formula, id="{index_var}", weight="{weight}", strata="{strata}", domain={domain_var}, model={model_var}, data_model=data_model, data_proj=data_proj, model_metric={parent.metric}, kfold={parent.k_fold}, grid={parent.grid})\n'
    else:
        if strata == 'NULL':
            r_script += f'model <- projection(formula, id="{index_var}", weight="{weight}", strata={strata}, domain="{domain_var}", model={model_var}, data_model=data_model, data_proj=data_proj, model_metric={parent.metric}, kfold={parent.k_fold}, grid={parent.grid})\n'
        else:
            r_script += f'model <- projection(formula, id="{index_var}", weight="{weight}", strata="{strata}", domain="{domain_var}", model={model_var}, data_model=data_model, data_proj=data_proj, model_metric={parent.metric}, kfold={parent.k_fold}, grid={parent.grid})\n'
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

    # method_label = QLabel("Stepwise Selection Method:")
    # layout.addWidget(method_label)

    # parent.method_combo = QComboBox()
    # parent.method_combo.addItems(["None", "Stepwise", "Forward", "Backward"])
    # layout.addWidget(parent.method_combo)

    model_metric_label = QLabel("Model Metric:")
    layout.addWidget(model_metric_label)

    parent.model_metric_combo = QComboBox()
    parent.model_metric_combo.addItems(["yardstick::metric_set()", "NULL"])
    parent.model_metric_combo.setCurrentText("NULL")
    layout.addWidget(parent.model_metric_combo)

    kfold_label = QLabel("The number of partitions :")
    layout.addWidget(kfold_label)

    parent.kfold_edit = QLineEdit()
    parent.kfold_edit.setValidator(QIntValidator())
    parent.kfold_edit.setText("3")
    layout.addWidget(parent.kfold_edit)

    grid_label = QLabel("Grid:")
    layout.addWidget(grid_label)

    parent.grid_edit = QLineEdit()
    parent.grid_edit.setValidator(QIntValidator())
    parent.grid_edit.setText("10")
    layout.addWidget(parent.grid_edit)
    
    epoch_label = QLabel("Epoch")
    epoch_label.setVisible(False)
    layout.addWidget(epoch_label)
    
    parent.epoch_edit = QLineEdit()
    parent.epoch_edit.setValidator(QIntValidator())
    parent.epoch_edit.setText("10")
    parent.epoch_edit.setVisible(False)
    layout.addWidget(parent.epoch_edit)
    
    hidden_unit_label = QLabel("Hidden Unit")
    hidden_unit_label.setVisible(False)
    layout.addWidget(hidden_unit_label)
    
    parent.hidden_edit = QLineEdit()
    parent.hidden_edit.setVisible(False)
    parent.hidden_edit.setValidator(QIntValidator())
    parent.hidden_edit.setText("5")
    layout.addWidget(parent.hidden_edit)
    
    learning_label = QLabel("Learning Rate")
    learning_label.setVisible(False)
    layout.addWidget(learning_label)
    
    parent.learning_edit = QLineEdit()
    parent.learning_edit.setVisible(False)
    parent.learning_edit.setValidator(QDoubleValidator())
    parent.learning_edit.setText("0.01")
    layout.addWidget(parent.learning_edit)
    
    if(parent.projection_method=="Neural Network"):
        epoch_label.setVisible(True)
        parent.epoch_edit.setVisible(True)
        hidden_unit_label.setVisible(True)
        parent.hidden_edit.setVisible(True)
        learning_label.setVisible(True)
        parent.learning_edit.setVisible(True)
    

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
    parent.metric = parent.model_metric_combo.currentText()
    parent.k_fold = parent.kfold_edit.text()
    parent.grid = parent.grid_edit.text()
    parent.epoch = parent.epoch_edit.text()
    parent.hidden_unit = parent.hidden_edit.text()
    parent.learning_rate = parent.learning_edit.text()
    dialog.accept()
    show_r_script(parent)


import unittest
from unittest.mock import MagicMock
import sys

class MockParent:
    def __init__(self):
        self.of_interest_var = ["var1 [Numeric]"]
        self.auxilary_vars = ["var2 [Numeric]", "var3 [Numeric]"]
        self.as_factor_var = ["var4 [String]"]
        self.index_var = ["var5 [Numeric]"]
        self.domain_var = ["var6 [Numeric]"]
        self.weight_var = ["var7 [Numeric]"]
        self.strata_var = ["var8 [Numeric]"]
        self.projection_method = "Linear"
        self.var_position = "After"
        self.selection_method = "None"
        self.metric = "yardstick::metric_set()"
        self.k_fold = "3"
        self.grid = "10"
        self.epoch = "10"
        self.hidden_unit = "5"
        self.learning_rate = "0.01"
        self.model_name = "model"
        self.projection_name = "projection"
        self.separator = "_"

class TestGenerateRScript(unittest.TestCase):
    def setUp(self):
        self.parent = MockParent()

    def test_generate_r_script_linear(self):
        self.parent.projection_method = "Linear"
        r_script = generate_r_script(self.parent)
        self.assertIn("linear_reg()", r_script)
        self.assertIn("var1 ~ var2 + var3 + var4", r_script)

    def test_generate_r_script_logistic(self):
        self.parent.projection_method = "Logistic"
        r_script = generate_r_script(self.parent)
        self.assertIn("logistic_reg()", r_script)
        self.assertIn("var1 ~ var2 + var3 + var4", r_script)

    def test_generate_r_script_svm_linear(self):
        self.parent.projection_method = "SVM Linear"
        r_script = generate_r_script(self.parent)
        self.assertIn("svm_linear(mode='classification')", r_script)
        self.assertIn("var1 ~ var2 + var3 + var4", r_script)

    def test_generate_r_script_svm_rbf(self):
        self.parent.projection_method = "SVM RBF"
        r_script = generate_r_script(self.parent)
        self.assertIn("svm_rbf(mode='classification')", r_script)
        self.assertIn("var1 ~ var2 + var3 + var4", r_script)

    def test_generate_r_script_neural_network(self):
        self.parent.projection_method = "Neural Network"
        r_script = generate_r_script(self.parent)
        self.assertIn("mlp(mode='classification', engine='nnet', epochs=10, hidden_units=5, learn_rate=0.01)", r_script)
        self.assertIn("var1 ~ var2 + var3 + var4", r_script)

    def test_generate_r_script_gradient_boost(self):
        self.parent.projection_method = "Gradient Boost"
        r_script = generate_r_script(self.parent)
        self.assertIn("boost_tree(", r_script)
        self.assertIn("var1 ~ var2 + var3 + var4", r_script)
    
    def test_assign_of_interest_with_numeric(self):

        # Setup mocks
        index = MagicMock()
        index.data.return_value = "variable1 [Numeric]"
        self.parent.variables_list = MagicMock()
        self.parent.variables_list.selectedIndexes.return_value = [index]
        self.parent.of_interest_model = MagicMock()
        self.parent.variables_list.model = MagicMock(return_value=MagicMock())
        self.parent.variables_list.model().removeRow = MagicMock()
        self.parent.projection_method = "Linear"
        self.parent.of_interest_var = []
        self.parent.r_script_edit = MagicMock()
        self.parent.of_interest_model.setStringList = MagicMock()
        
        sys.modules[__name__].show_r_script = MagicMock()

        assign_of_interest(self.parent)

        self.assertEqual(self.parent.of_interest_var, ["variable1 [Numeric]"])
        self.parent.of_interest_model.setStringList.assert_called_with(["variable1 [Numeric]"])
        self.parent.variables_list.model().removeRow.assert_called_once()
    
    def test_assign_of_interest_with_string(self):
        # Setup mocks
        index = MagicMock()
        index.data.return_value = "variable1 [String]"
        self.parent.variables_list = MagicMock()
        self.parent.variables_list.selectedIndexes.return_value = [index]
        self.parent.projection_method = "Linear"
        self.parent.of_interest_var = []
        
        sys.modules[__name__].show_r_script = MagicMock()

        msg_box_instance = MagicMock()
        msg_box_class = MagicMock(return_value=msg_box_instance)
        original_qmessagebox = QMessageBox
        sys.modules[__name__].QMessageBox = msg_box_class

        assign_of_interest(self.parent)

        msg_box_instance.setIcon.assert_called_once()
        msg_box_instance.setText.assert_called_once_with("All selected variables are of type String. Variable of interest must be of type Numeric.")
        msg_box_instance.setWindowTitle.assert_called_once_with("Warning")
        msg_box_instance.exec.assert_called_once()

        sys.modules[__name__].QMessageBox = original_qmessagebox
        
    def test_assign_auxilary(self):
        # Setup mocks
        index1 = MagicMock()
        index1.data.return_value = "variable2 [Numeric]"
        self.parent.variables_list = MagicMock()
        self.parent.variables_list.selectedIndexes.return_value = [index1]
        self.parent.auxilary_model = MagicMock()
        self.parent.variables_list.model = MagicMock(return_value=MagicMock())
        self.parent.variables_list.model().removeRow = MagicMock()
        self.parent.auxilary_vars = []
        self.parent.r_script_edit = MagicMock()
        self.parent.auxilary_model.setStringList = MagicMock()

        sys.modules[__name__].show_r_script = MagicMock()

        assign_auxilary(self.parent)

        self.assertEqual(self.parent.auxilary_vars, ["variable2 [Numeric]"])
        self.parent.auxilary_model.setStringList.assert_called_with(["variable2 [Numeric]"])
        self.parent.variables_list.model().removeRow.assert_called()
    
    def test_assign_auxilary_no_numeric(self):
        # Setup mocks
        index1 = MagicMock()
        index1.data.return_value = "variable2 [String]"
        self.parent.variables_list = MagicMock()
        self.parent.variables_list.selectedIndexes.return_value = [index1]
        self.parent.auxilary_vars = []
        
        msg_box_instance = MagicMock()
        msg_box_class = MagicMock(return_value=msg_box_instance)
        original_qmessagebox = QMessageBox
        sys.modules[__name__].QMessageBox = msg_box_class

        assign_auxilary(self.parent)

        msg_box_instance.setIcon.assert_called_once()
        msg_box_instance.setText.assert_called_once_with("No valid numeric variables selected. Please select at least one numeric variable.")
        msg_box_instance.setWindowTitle.assert_called_once_with("Warning")
        msg_box_instance.exec.assert_called_once()

        sys.modules[__name__].QMessageBox = original_qmessagebox
    
    def test_assign_index(self):
        # Setup mocks
        index = MagicMock()
        index.data.return_value = "variable5 [Numeric]"
        self.parent.variables_list = MagicMock()
        self.parent.variables_list.selectedIndexes.return_value = [index]
        self.parent.index_model = MagicMock()
        self.parent.variables_list.model = MagicMock(return_value=MagicMock())
        self.parent.variables_list.model().removeRow = MagicMock()
        self.parent.index_var = []
        self.parent.r_script_edit = MagicMock()
        self.parent.index_model.setStringList = MagicMock()

        sys.modules[__name__].show_r_script = MagicMock()

        assign_index(self.parent)

        self.assertEqual(self.parent.index_var, ["variable5 [Numeric]"])
        self.parent.index_model.setStringList.assert_called_with(["variable5 [Numeric]"])
        self.parent.variables_list.model().removeRow.assert_called_once()
    
    def test_assign_strata(self):
        # Setup mocks
        index = MagicMock()
        index.data.return_value = "variable8 [Numeric]"
        self.parent.variables_list = MagicMock()
        self.parent.variables_list.selectedIndexes.return_value = [index]
        self.parent.strata_model = MagicMock()
        self.parent.variables_list.model = MagicMock(return_value=MagicMock())
        self.parent.variables_list.model().removeRow = MagicMock()
        self.parent.strata_var = []
        self.parent.r_script_edit = MagicMock()
        self.parent.strata_model.setStringList = MagicMock()

        sys.modules[__name__].show_r_script = MagicMock()

        assign_strata(self.parent)

        self.assertEqual(self.parent.strata_var, ["variable8 [Numeric]"])
        self.parent.strata_model.setStringList.assert_called_with(["variable8 [Numeric]"])
        self.parent.variables_list.model().removeRow.assert_called_once()
    
    def test_assign_weight(self):
        # Setup mocks
        index = MagicMock()
        index.data.return_value = "variable7 [Numeric]"
        self.parent.variables_list = MagicMock()
        self.parent.variables_list.selectedIndexes.return_value = [index]
        self.parent.weight_model = MagicMock()
        self.parent.variables_list.model = MagicMock(return_value=MagicMock())
        self.parent.variables_list.model().removeRow = MagicMock()
        self.parent.weight_var = []
        self.parent.r_script_edit = MagicMock()
        self.parent.weight_model.setStringList = MagicMock()

        sys.modules[__name__].show_r_script = MagicMock()

        assign_weight(self.parent)

        self.assertEqual(self.parent.weight_var, ["variable7 [Numeric]"])
        self.parent.weight_model.setStringList.assert_called_with(["variable7 [Numeric]"])
        self.parent.variables_list.model().removeRow.assert_called_once()
    
    def test_assign_weight_string(self):
        # Setup mocks
        index = MagicMock()
        index.data.return_value = "variable7 [String]"
        self.parent.variables_list = MagicMock()
        self.parent.variables_list.selectedIndexes.return_value = [index]
        self.parent.weight_var = []
        
        msg_box_instance = MagicMock()
        msg_box_class = MagicMock(return_value=msg_box_instance)
        original_qmessagebox = QMessageBox
        sys.modules[__name__].QMessageBox = msg_box_class

        assign_weight(self.parent)

        msg_box_instance.setIcon.assert_called_once()
        msg_box_instance.setText.assert_called_once_with("All selected variables are of type String. Weight variable must be of type Numeric.")
        msg_box_instance.setWindowTitle.assert_called_once_with("Warning")
        msg_box_instance.exec.assert_called_once()

        sys.modules[__name__].QMessageBox = original_qmessagebox
    
    def test_unassign_variable(self):
        # Setup mocks
        self.parent.of_interest_list = MagicMock()
        self.parent.of_interest_list.selectedIndexes.return_value = [MagicMock(data=MagicMock(return_value="variable1 [Numeric]"))]
        self.parent.variables_list = MagicMock()
        self.parent.variables_list.model = MagicMock(return_value=MagicMock())
        self.parent.variables_list.model().insertRow = MagicMock()
        self.parent.of_interest_var = ["variable1 [Numeric]"]
        self.parent.of_interest_model = MagicMock()
        self.parent.of_interest_model.setStringList = MagicMock()

        sys.modules[__name__].show_r_script = MagicMock()

        unassign_variable(self.parent)

        self.assertEqual(self.parent.of_interest_var, [])
        self.parent.of_interest_model.setStringList.assert_called_with([])
        self.parent.variables_list.model().insertRow.assert_called_once()
    
    def test_generate_r_script(self):
        self.parent.of_interest_var = ["variable1 [Numeric]"]
        self.parent.auxilary_vars = ["variable2 [Numeric]"]
        self.parent.as_factor_var = ["variable4 [String]"]
        self.parent.index_var = ["index1 [Numeric]"]
        self.parent.domain_var = ["domain1 [Numeric]"]
        self.parent.weight_var = ["weight1 [Numeric]"]
        self.parent.strata_var = ["strata1 [Numeric]"]
        self.parent.projection_method = "Linear"
        self.parent.var_position = "After"
        self.parent.selection_method = "None"
        self.parent.metric = "yardstick::metric_set()"
        self.parent.k_fold = "3"
        self.parent.grid = "10"
        self.parent.epoch = "10"
        self.parent.hidden_unit = "5"
        self.parent.learning_rate = "0.01"
        self.parent.model_name = "model"
        self.parent.projection_name = "projection"
        self.parent.separator = "_"

        r_script = generate_r_script(self.parent)

        # Cek bagian-bagian penting dari skrip
        self.assertIn('formula <- variable1 ~ variable2 + variable4', r_script)
        self.assertIn('linear_reg()', r_script)
        self.assertIn('data_model <- data.frame(variable2, variable4, variable1, domain1, index1, strata1, weight1);', r_script)
        self.assertIn('model <- projection(formula', r_script)
        self.assertIn('model_metric=yardstick::metric_set()', r_script)
        self.assertIn('kfold=3', r_script)
        self.assertIn('grid=10', r_script)
    
    def test_generate_r_script_with_empty_interest_of_var(self):
        self.parent.of_interest_var = []
        self.parent.auxilary_vars = ["variable2 [Numeric]"]
        self.parent.as_factor_var = ["variable4 [String]"]
        self.parent.index_var = ["index1 [Numeric]"]
        self.parent.domain_var = ["domain1 [Numeric]"]
        self.parent.weight_var = ["weight1 [Numeric]"]
        self.parent.strata_var = ["strata1 [Numeric]"]
        self.parent.projection_method = "Linear"
        self.parent.var_position = "After"
        self.parent.selection_method = "None"
        self.parent.metric = "yardstick::metric_set()"
        self.parent.k_fold = "3"
        self.parent.grid = "10"
        self.parent.epoch = "10"
        self.parent.hidden_unit = "5"
        self.parent.learning_rate = "0.01"
        self.parent.model_name = "model"
        self.parent.projection_name = "projection"
        self.parent.separator = "_"

        r_script = generate_r_script(self.parent)

        # Cek bagian-bagian penting dari skrip
        self.assertIn('formula <-  ~ variable2 + variable4', r_script)
        self.assertIn('linear_reg()', r_script)
        self.assertIn('data_model <- data.frame(variable2, variable4, domain1, index1, strata1, weight1);', r_script)
        self.assertIn('model <- projection(formula', r_script)
        self.assertIn('model_metric=yardstick::metric_set()', r_script)
        self.assertIn('kfold=3', r_script)
        self.assertIn('grid=10', r_script)
    
    def test_generate_r_script_with_multiple_of_interest(self):
        self.parent.of_interest_var = ["variable1 [Numeric]", "variabel y [Numeric]"]
        self.parent.auxilary_vars = ["variable2 [Numeric]"]
        self.parent.as_factor_var = ["variable4 [String]"]
        self.parent.index_var = ["index1 [Numeric]"]
        self.parent.domain_var = ["domain1 [Numeric]"]
        self.parent.weight_var = ["weight1 [Numeric]"]
        self.parent.strata_var = ["strata1 [Numeric]"]
        self.parent.projection_method = "Linear"
        self.parent.var_position = "After"
        self.parent.selection_method = "None"
        self.parent.metric = "yardstick::metric_set()"
        self.parent.k_fold = "3"
        self.parent.grid = "10"
        self.parent.epoch = "10"
        self.parent.hidden_unit = "5"
        self.parent.learning_rate = "0.01"
        self.parent.model_name = "model"
        self.parent.projection_name = "projection"
        self.parent.separator = "_"

        r_script = generate_r_script(self.parent)

        # Cek bagian-bagian penting dari skrip
        self.assertIn('formula <- variable1 ~ variable2 + variable4', r_script)
        self.assertIn('linear_reg()', r_script)
        self.assertIn('data_model <- data.frame(variable2, variable4, variable1, variabel_y, domain1, index1, strata1, weight1);', r_script)
        self.assertIn('model <- projection(formula', r_script)
        self.assertIn('model_metric=yardstick::metric_set()', r_script)
        self.assertIn('kfold=3', r_script)
        self.assertIn('grid=10', r_script)
    
    def test_generate_r_script_with_multiple_auxalary(self):
        self.parent.of_interest_var = ["variabley [Numeric]"]
        self.parent.auxilary_vars = ["variable2 [Numeric]", "variabel5 [Numeric]"]
        self.parent.as_factor_var = ["variable4 [String]"]
        self.parent.index_var = ["index1 [Numeric]"]
        self.parent.domain_var = ["domain1 [Numeric]"]
        self.parent.weight_var = ["weight1 [Numeric]"]
        self.parent.strata_var = ["strata1 [Numeric]"]
        self.parent.projection_method = "Linear"
        self.parent.var_position = "After"
        self.parent.selection_method = "None"
        self.parent.metric = "yardstick::metric_set()"
        self.parent.k_fold = "3"
        self.parent.grid = "10"
        self.parent.epoch = "10"
        self.parent.hidden_unit = "5"
        self.parent.learning_rate = "0.01"
        self.parent.model_name = "model"
        self.parent.projection_name = "projection"
        self.parent.separator = "_"

        r_script = generate_r_script(self.parent)

        # Cek bagian-bagian penting dari skrip
        self.assertIn('formula <- variabley ~ variable2 + variabel5 + variable4', r_script)
        self.assertIn('linear_reg()', r_script)
        self.assertIn('data_model <- data.frame(variable2, variabel5, variable4, variabley, domain1, index1, strata1, weight1);', r_script)
        self.assertIn('model <- projection(formula', r_script)
        self.assertIn('model_metric=yardstick::metric_set()', r_script)
        self.assertIn('kfold=3', r_script)
        self.assertIn('grid=10', r_script)
    
    def generate_r_script_multiple_as_factor(self):
        self.parent.of_interest_var = ["variabley [Numeric]"]
        self.parent.auxilary_vars = ["variable2 [Numeric]"]
        self.parent.as_factor_var = ["variabel5 [Numeric]", "variable4 [String]"]
        self.parent.index_var = ["index1 [Numeric]"]
        self.parent.domain_var = ["domain1 [Numeric]"]
        self.parent.weight_var = ["weight1 [Numeric]"]
        self.parent.strata_var = ["strata1 [Numeric]"]
        self.parent.projection_method = "Linear"
        self.parent.var_position = "After"
        self.parent.selection_method = "None"
        self.parent.metric = "yardstick::metric_set()"
        self.parent.k_fold = "3"
        self.parent.grid = "10"
        self.parent.epoch = "10"
        self.parent.hidden_unit = "5"
        self.parent.learning_rate = "0.01"
        self.parent.model_name = "model"
        self.parent.projection_name = "projection"
        self.parent.separator = "_"

        r_script = generate_r_script(self.parent)

        # Cek bagian-bagian penting dari skrip
        self.assertIn('formula <- variabley ~ variable2 + variabel5 + variable4', r_script)
        self.assertIn('linear_reg()', r_script)
        self.assertIn('data_model <- data.frame(variable2, variabel5, variable4, variabley, domain1, index1, strata1, weight1);', r_script)
        self.assertIn('model <- projection(formula', r_script)
        self.assertIn('model_metric=yardstick::metric_set()', r_script)
        self.assertIn('kfold=3', r_script)
        self.assertIn('grid=10', r_script)
    
    def test_generate_r_script_with_no_as_factor(self):
        self.parent.of_interest_var = ["variabley [Numeric]"]
        self.parent.auxilary_vars = ["variable2 [Numeric]", "variabel5 [Numeric]"]
        self.parent.as_factor_var = []
        self.parent.index_var = ["index1 [Numeric]"]
        self.parent.domain_var = ["domain1 [Numeric]"]
        self.parent.weight_var = ["weight1 [Numeric]"]
        self.parent.strata_var = ["strata1 [Numeric]"]
        self.parent.projection_method = "Linear"
        self.parent.var_position = "After"
        self.parent.selection_method = "None"
        self.parent.metric = "yardstick::metric_set()"
        self.parent.k_fold = "3"
        self.parent.grid = "10"
        self.parent.epoch = "10"
        self.parent.hidden_unit = "5"
        self.parent.learning_rate = "0.01"
        self.parent.model_name = "model"
        self.parent.projection_name = "projection"
        self.parent.separator = "_"

        r_script = generate_r_script(self.parent)

        # Cek bagian-bagian penting dari skrip
        self.assertIn('formula <- variabley ~ variable2 + variabel5', r_script)
        self.assertIn('linear_reg()', r_script)
        self.assertIn('data_model <- data.frame(variable2, variabel5, variabley, domain1, index1, strata1, weight1);', r_script)
        self.assertIn('model <- projection(formula', r_script)
        self.assertIn('model_metric=yardstick::metric_set()', r_script)
        self.assertIn('kfold=3', r_script)
        self.assertIn('grid=10', r_script)
        
    def generate_r_script_with_no_index(self):
        self.parent.of_interest_var = ["variabley [Numeric]"]
        self.parent.auxilary_vars = ["variable2 [Numeric]", "variabel5 [Numeric]"]
        self.parent.as_factor_var = ["variable4 [String]"]
        self.parent.index_var = []
        self.parent.domain_var = ["domain1 [Numeric]"]
        self.parent.weight_var = ["weight1 [Numeric]"]
        self.parent.strata_var = ["strata1 [Numeric]"]
        self.parent.projection_method = "Linear"
        self.parent.var_position = "After"
        self.parent.selection_method = "None"
        self.parent.metric = "yardstick::metric_set()"
        self.parent.k_fold = "3"
        self.parent.grid = "10"
        self.parent.epoch = "10"
        self.parent.hidden_unit = "5"
        self.parent.learning_rate = "0.01"
        self.parent.model_name = "model"
        self.parent.projection_name = "projection"
        self.parent.separator = "_"

        r_script = generate_r_script(self.parent)

        # Cek bagian-bagian penting dari skrip
        self.assertIn('formula <- variabley ~ variable2 + variabel5 + variable4', r_script)
        self.assertIn('linear_reg()', r_script)
        self.assertIn('data_model <- data.frame(variable2, variabel5, variable4, variabley, domain1, strata1, weight1);', r_script)
        self.assertIn('model <- projection(formula', r_script)
        self.assertIn('model_metric=yardstick::metric_set()', r_script)
        self.assertIn('kfold=3', r_script)
        self.assertIn('grid=10', r_script)
    
    def test_generate_r_script_with_multiple_index(self):
        self.parent.of_interest_var = ["variabley [Numeric]"]
        self.parent.auxilary_vars = ["variable2 [Numeric]", "variabel5 [Numeric]"]
        self.parent.as_factor_var = ["variable4 [String]"]
        self.parent.index_var = ["index1 [Numeric]", "index2 [Numeric]"]
        self.parent.domain_var = ["domain1 [Numeric]"]
        self.parent.weight_var = ["weight1 [Numeric]"]
        self.parent.strata_var = ["strata1 [Numeric]"]
        self.parent.projection_method = "Linear"
        self.parent.var_position = "After"
        self.parent.selection_method = "None"
        self.parent.metric = "yardstick::metric_set()"
        self.parent.k_fold = "3"
        self.parent.grid = "10"
        self.parent.epoch = "10"
        self.parent.hidden_unit = "5"
        self.parent.learning_rate = "0.01"
        self.parent.model_name = "model"
        self.parent.projection_name = "projection"
        self.parent.separator = "_"

        r_script = generate_r_script(self.parent)

        # Cek bagian-bagian penting dari skrip
        self.assertIn('formula <- variabley ~ variable2 + variabel5 + variable4', r_script)
        self.assertIn('linear_reg()', r_script)
        self.assertIn('data_model <- data.frame(variable2, variabel5, variable4, variabley, domain1, index1, index2, strata1, weight1);', r_script)
        self.assertIn('model <- projection(formula', r_script)
        self.assertIn('model_metric=yardstick::metric_set()', r_script)
        self.assertIn('kfold=3', r_script)
        self.assertIn('grid=10', r_script)
    
    def test_generate_r_script_with_multiple_domain(self):
        self.parent.of_interest_var = ["variabley [Numeric]"]
        self.parent.auxilary_vars = ["variable2 [Numeric]", "variabel5 [Numeric]"]
        self.parent.as_factor_var = ["variable4 [String]"]
        self.parent.index_var = ["index1 [Numeric]"]
        self.parent.domain_var = ["domain1 [Numeric]", "domain2 [Numeric]"]
        self.parent.weight_var = ["weight1 [Numeric]"]
        self.parent.strata_var = ["strata1 [Numeric]"]
        self.parent.projection_method = "Linear"
        self.parent.var_position = "After"
        self.parent.selection_method = "None"
        self.parent.metric = "yardstick::metric_set()"
        self.parent.k_fold = "3"
        self.parent.grid = "10"
        self.parent.epoch = "10"
        self.parent.hidden_unit = "5"
        self.parent.learning_rate = "0.01"
        self.parent.model_name = "model"
        self.parent.projection_name = "projection"
        self.parent.separator = "_"

        r_script = generate_r_script(self.parent)

        # Cek bagian-bagian penting dari skrip
        self.assertIn('formula <- variabley ~ variable2 + variabel5 + variable4', r_script)
        self.assertIn('linear_reg()', r_script)
        self.assertIn('data_model <- data.frame(variable2, variabel5, variable4, variabley, domain1, domain2, index1, strata1, weight1);', r_script)
        self.assertIn('model <- projection(formula', r_script)
        self.assertIn('model_metric=yardstick::metric_set()', r_script)
        self.assertIn('kfold=3', r_script)
        self.assertIn('grid=10', r_script)
    
    def test_generate_r_script_with_no_weight(self):
        self.parent.of_interest_var = ["variabley [Numeric]"]
        self.parent.auxilary_vars = ["variable2 [Numeric]", "variabel5 [Numeric]"]
        self.parent.as_factor_var = ["variable4 [String]"]
        self.parent.index_var = ["index1 [Numeric]"]
        self.parent.domain_var = ["domain1 [Numeric]"]
        self.parent.weight_var = []
        self.parent.strata_var = ["strata1 [Numeric]"]
        self.parent.projection_method = "Linear"
        self.parent.var_position = "After"
        self.parent.selection_method = "None"
        self.parent.metric = "yardstick::metric_set()"
        self.parent.k_fold = "3"
        self.parent.grid = "10"
        self.parent.epoch = "10"
        self.parent.hidden_unit = "5"
        self.parent.learning_rate = "0.01"
        self.parent.model_name = "model"
        self.parent.projection_name = "projection"
        self.parent.separator = "_"

        r_script = generate_r_script(self.parent)

        # Cek bagian-bagian penting dari skrip
        self.assertIn('formula <- variabley ~ variable2 + variabel5 + variable4', r_script)
        self.assertIn('linear_reg()', r_script)
        self.assertIn('data_model <- data.frame(variable2, variabel5, variable4, variabley, domain1, index1, strata1);', r_script)
        self.assertIn('model <- projection(formula', r_script)
        self.assertIn('model_metric=yardstick::metric_set()', r_script)
        self.assertIn('kfold=3', r_script)
        self.assertIn('grid=10', r_script)
        
    def test_generate_r_script_with_multiple_weight(self):
        self.parent.of_interest_var = ["variabley [Numeric]"]
        self.parent.auxilary_vars = ["variable2 [Numeric]", "variabel5 [Numeric]"]
        self.parent.as_factor_var = ["variable4 [String]"]
        self.parent.index_var = ["index1 [Numeric]"]
        self.parent.domain_var = ["domain1 [Numeric]"]
        self.parent.weight_var = ["weight1 [Numeric]", "weight2 [Numeric]"]
        self.parent.strata_var = ["strata1 [Numeric]"]
        self.parent.projection_method = "Linear"
        self.parent.var_position = "After"
        self.parent.selection_method = "None"
        self.parent.metric = "yardstick::metric_set()"
        self.parent.k_fold = "3"
        self.parent.grid = "10"
        self.parent.epoch = "10"
        self.parent.hidden_unit = "5"
        self.parent.learning_rate = "0.01"
        self.parent.model_name = "model"
        self.parent.projection_name = "projection"
        self.parent.separator = "_"

        r_script = generate_r_script(self.parent)

        # Cek bagian-bagian penting dari skrip
        self.assertIn('formula <- variabley ~ variable2 + variabel5 + variable4', r_script)
        self.assertIn('linear_reg()', r_script)
        self.assertIn('data_model <- data.frame(variable2, variabel5, variable4, variabley, domain1, index1, strata1, weight1, weight2);', r_script)
        self.assertIn('model <- projection(formula', r_script)
        self.assertIn('model_metric=yardstick::metric_set()', r_script)
        self.assertIn('kfold=3', r_script)
        self.assertIn('grid=10', r_script)
    
    def test_generate_r_script_with_no_strata(self):
        self.parent.of_interest_var = ["variabley [Numeric]"]
        self.parent.auxilary_vars = ["variable2 [Numeric]", "variabel5 [Numeric]"]
        self.parent.as_factor_var = ["variable4 [String]"]
        self.parent.index_var = ["index1 [Numeric]"]
        self.parent.domain_var = ["domain1 [Numeric]"]
        self.parent.weight_var = ["weight1 [Numeric]"]
        self.parent.strata_var = []
        self.parent.projection_method = "Linear"
        self.parent.var_position = "After"
        self.parent.selection_method = "None"
        self.parent.metric = "yardstick::metric_set()"
        self.parent.k_fold = "3"
        self.parent.grid = "10"
        self.parent.epoch = "10"
        self.parent.hidden_unit = "5"
        self.parent.learning_rate = "0.01"
        self.parent.model_name = "model"
        self.parent.projection_name = "projection"
        self.parent.separator = "_"

        r_script = generate_r_script(self.parent)

        # Cek bagian-bagian penting dari skrip
        self.assertIn('formula <- variabley ~ variable2 + variabel5 + variable4', r_script)
        self.assertIn('linear_reg()', r_script)
        self.assertIn('data_model <- data.frame(variable2, variabel5, variable4, variabley, domain1, index1, weight1);', r_script)
        self.assertIn('model <- projection(formula', r_script)
        self.assertIn('model_metric=yardstick::metric_set()', r_script)
        self.assertIn('kfold=3', r_script)
        self.assertIn('grid=10', r_script)
    
    def test_generate_r_script_with_multiple_strata(self):
        self.parent.of_interest_var = ["variabley [Numeric]"]
        self.parent.auxilary_vars = ["variable2 [Numeric]", "variabel5 [Numeric]"]
        self.parent.as_factor_var = ["variable4 [String]"]
        self.parent.index_var = ["index1 [Numeric]"]
        self.parent.domain_var = ["domain1 [Numeric]"]
        self.parent.weight_var = ["weight1 [Numeric]"]
        self.parent.strata_var = ["strata1 [Numeric]", "strata2 [Numeric]"]
        self.parent.projection_method = "Linear"
        self.parent.var_position = "After"
        self.parent.selection_method = "None"
        self.parent.metric = "yardstick::metric_set()"
        self.parent.k_fold = "3"
        self.parent.grid = "10"
        self.parent.epoch = "10"
        self.parent.hidden_unit = "5"
        self.parent.learning_rate = "0.01"
        self.parent.model_name = "model"
        self.parent.projection_name = "projection"
        self.parent.separator = "_"

        r_script = generate_r_script(self.parent)

        # Cek bagian-bagian penting dari skrip
        self.assertIn('formula <- variabley ~ variable2 + variabel5 + variable4', r_script)
        self.assertIn('linear_reg()', r_script)
        self.assertIn('data_model <- data.frame(variable2, variabel5, variable4, variabley, domain1, index1, strata1, strata2, weight1);', r_script)
        self.assertIn('model <- projection(formula', r_script)
        self.assertIn('model_metric=yardstick::metric_set()', r_script)
        self.assertIn('kfold=3', r_script)
        self.assertIn('grid=10', r_script)
        

if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)
    unittest.main()