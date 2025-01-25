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
    selected_indexes = parent.of_interest_list.selectedIndexes()
    if selected_indexes:
        selected_items = [index.data() for index in selected_indexes]
        parent.of_interest_var = [var for var in parent.of_interest_var if var not in selected_items]
        parent.of_interest_model.setStringList(parent.of_interest_var)
        parent.variables_list.model().insertRow(0)  # Add back to variables list
        parent.variables_list.model().setData(parent.variables_list.model().index(0), selected_items[0])
        return

    selected_indexes = parent.auxilary_list.selectedIndexes()
    if selected_indexes:
        selected_items = [index.data() for index in selected_indexes]
        parent.auxilary_vars = [var for var in parent.auxilary_vars if var not in selected_items]
        parent.auxilary_model.setStringList(parent.auxilary_vars)
        for item in selected_items:
            parent.variables_list.model().insertRow(0)  # Add back to variables list
            parent.variables_list.model().setData(parent.variables_list.model().index(0), item)
        return

    selected_indexes = parent.vardir_list.selectedIndexes()
    if selected_indexes:
        selected_items = [index.data() for index in selected_indexes]
        parent.vardir_var = [var for var in parent.vardir_var if var not in selected_items]
        parent.vardir_model.setStringList(parent.vardir_var)
        for item in selected_items:
            parent.variables_list.model().insertRow(0)  # Add back to variables list
            parent.variables_list.model().setData(parent.variables_list.model().index(0), item)
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
    auxilary_vars = " + ".join([var.split(" [")[0].replace(" ", "_") for var in parent.auxilary_vars])
    vardir_var = f'{parent.vardir_var[0].split(" [")[0].replace(" ", "_")}' if parent.vardir_var else '""'
    as_factor_var = " + ".join([f'as.factor({var.split(" [")[0].replace(" ", "_")})' for var in parent.as_factor_var]) if parent.as_factor_var else '""'
    
    if auxilary_vars and as_factor_var:
        formula = f'{of_interest_var} ~ {auxilary_vars} + {as_factor_var}'
    elif auxilary_vars:
        formula = f'{of_interest_var} ~ {auxilary_vars}'
    elif as_factor_var:
        formula = f'{of_interest_var} ~ {as_factor_var}'
    else:
        formula = f'{of_interest_var} ~ 1'  # Default formula if no auxilary or major area variables

    r_script = f'names(data) <- gsub(" ", "_", names(data)); #Replace space with underscore\n'
    r_script += f'formula <- {formula}\n'
    r_script += f'vardir_var <- data["{vardir_var}"]\n'
    if parent.selection_method and parent.selection_method != "None" and auxilary_vars:
        r_script += f'stepwise_model <- step(formula, direction="{parent.selection_method.lower()}")\n'
        r_script += f'final_formula <- formula(stepwise_model)\n'
        r_script += f'model<-mseFH(final_formula, {vardir_var}, method = "{parent.method}", data=data)'
    else:
        r_script += f'model<-mseFH(formula, {vardir_var}, method = "{parent.method}", data=data)'
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

    ok_button.clicked.connect(lambda: set_selection_method(parent, options_dialog))
    cancel_button.clicked.connect(options_dialog.reject)

    options_dialog.exec()

def set_selection_method(parent, dialog):
    parent.selection_method = parent.method_combo.currentText()
    parent.method = parent.method_selection.currentText()
    parent.precision = parent.precision_input.text()
    parent.B = parent.B_input.text()
    dialog.accept()
    show_r_script(parent)