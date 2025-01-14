from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QListView, QPushButton, QHBoxLayout, QAbstractItemView, QTextEdit, QComboBox, QLineEdit
from PyQt6.QtGui import QDoubleValidator, QIntValidator

def assign_dependent(parent):
    selected_indexes = parent.variables_list.selectedIndexes()
    if selected_indexes:
        parent.dependent_var = [selected_indexes[-1].data()]  # Only allow one dependent variable
        parent.dependent_model.setStringList(parent.dependent_var)
        parent.variables_list.model().removeRow(selected_indexes[-1].row())  # Remove from variables list
        show_r_script(parent)

def assign_independent(parent):
    selected_indexes = parent.variables_list.selectedIndexes()
    if selected_indexes:
        new_vars = [index.data() for index in selected_indexes]
        parent.independent_vars = list(set(parent.independent_vars + new_vars))  # Add new variables if they are different
        parent.independent_model.setStringList(parent.independent_vars)
        for index in selected_indexes:
            parent.variables_list.model().removeRow(index.row())  # Remove from variables list
        show_r_script(parent)

def assign_vardir(parent):
    selected_indexes = parent.variables_list.selectedIndexes()
    if selected_indexes:
        parent.vardir_var = [selected_indexes[-1].data()]
        parent.vardir_model.setStringList(parent.vardir_var)
        parent.variables_list.model().removeRow(selected_indexes[-1].row())  # Remove from variables list
        show_r_script(parent)

def unassign_variable(parent):
    selected_indexes = parent.dependent_list.selectedIndexes()
    if selected_indexes:
        selected_items = [index.data() for index in selected_indexes]
        parent.dependent_var = [var for var in parent.dependent_var if var not in selected_items]
        parent.dependent_model.setStringList(parent.dependent_var)
        parent.variables_list.model().insertRow(0)  # Add back to variables list
        parent.variables_list.model().setData(parent.variables_list.model().index(0), selected_items[0])
        return

    selected_indexes = parent.independent_list.selectedIndexes()
    if selected_indexes:
        selected_items = [index.data() for index in selected_indexes]
        parent.independent_vars = [var for var in parent.independent_vars if var not in selected_items]
        parent.independent_model.setStringList(parent.independent_vars)
        return

    selected_indexes = parent.vardir_list.selectedIndexes()
    if selected_indexes:
        selected_items = [index.data() for index in selected_indexes]
        parent.vardir_var = [var for var in parent.vardir_var if var not in selected_items]
        parent.vardir_model.setStringList(parent.vardir_var)
    show_r_script(parent)

def get_selected_variables(parent):
    return parent.dependent_var, parent.independent_vars, parent.vardir_var

def generate_r_script(parent):
    dependent_var = f'"{parent.dependent_var[0].split(" [")[0]}"' if parent.dependent_var else '""'
    independent_vars = " + ".join([f'"{var.split(" [")[0]}"' for var in parent.independent_vars])
    vardir_var = f'"{parent.vardir_var[0].split(" [")[0]}"' if parent.vardir_var else '""'
    formula = f'{dependent_var} ~ {independent_vars}'

    r_script = f'formula <- {formula}\n'
    if parent.stepwise_method and parent.stepwise_method != "None":
        r_script += f'stepwise_model <- step(formula, direction="{parent.stepwise_method.lower()}")\n'
        r_script += f'final_formula <- formula(stepwise_model)\n'
        r_script += f'mseFH(final_formula, {vardir_var}, method = "{parent.method}", MAXITER = 100, PRECISION = {parent.precision}, B = {parent.B}, data)'
    else:
        r_script += f'mseFH(formula, {vardir_var}, method = "{parent.method}", MAXITER = 100, PRECISION = {parent.precision}, B = {parent.B}, data)'
    return r_script

def show_r_script(parent):
    r_script = generate_r_script(parent)
    parent.r_script_edit.setText(r_script)

def get_script(parent):
    print(parent.r_script_edit.toPlainText())
    return parent.r_script_edit.toPlainText()  

def show_options(parent):
    options_dialog = QDialog(parent)
    options_dialog.setWindowTitle("Options")

    layout = QVBoxLayout()

    method_label = QLabel("Stepwise Selection Method:")
    layout.addWidget(method_label)

    parent.method_combo = QComboBox()
    parent.method_combo.addItems(["None", "Both", "Forward", "Backward"])
    layout.addWidget(parent.method_combo)

    method_label = QLabel("Method:")
    layout.addWidget(method_label)

    parent.method_selection = QComboBox()
    parent.method_selection.addItems(["ML", "REML", "FH"])
    parent.method_selection.setCurrentText("REML")
    layout.addWidget(parent.method_selection)

    precision_label = QLabel("Precision:")
    layout.addWidget(precision_label)

    parent.precision_input = QLineEdit()
    parent.precision_input.setValidator(QDoubleValidator(0.0, 1.0, 10))  # Allow only numbers from 0 to 1 with up to 10 decimal places
    parent.precision_input.setText("0.0001")
    layout.addWidget(parent.precision_input)

    B_label = QLabel("B:")
    layout.addWidget(B_label)

    parent.B_input = QLineEdit()
    parent.B_input.setValidator(QIntValidator(0, 10000))  # Allow only integer numbers
    parent.B_input.setText("0")
    layout.addWidget(parent.B_input)

    button_layout = QHBoxLayout()
    ok_button = QPushButton("OK")
    cancel_button = QPushButton("Cancel")
    button_layout.addWidget(ok_button)
    button_layout.addWidget(cancel_button)

    layout.addLayout(button_layout)

    options_dialog.setLayout(layout)

    ok_button.clicked.connect(lambda: set_stepwise_method(parent, options_dialog))
    cancel_button.clicked.connect(options_dialog.reject)

    options_dialog.exec()

def set_stepwise_method(parent, dialog):
    parent.stepwise_method = parent.method_combo.currentText()
    parent.method = parent.method_selection.currentText()
    parent.precision = parent.precision_input.text()
    parent.B = parent.B_input.text()
    dialog.accept()
    show_r_script(parent)  