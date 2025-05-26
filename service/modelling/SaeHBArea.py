from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QLineEdit
from PyQt6.QtGui import QIntValidator
from PyQt6.QtWidgets import QMessageBox

def assign_of_interest(parent):
    """
    Assigns a variable of interest from the selected variables in the parent object's variables list.
    This function checks the selected variables in the parent object's variables list. If any of the selected
    variables are not of type "String", it assigns the first non-string variable as the variable of interest,
    updates the parent object's of_interest_model with this variable, and removes the variable from the variables list.
    If all selected variables are of type "String", it displays a warning message.
    Args:
        parent: The parent object containing the variables list and other related attributes.
    Attributes:
        parent.variables_list: The list of variables from which the variable of interest is selected.
        parent.of_interest_var: The variable of interest to be assigned.
        parent.of_interest_model: The model to be updated with the variable of interest.
    Raises:
        QMessageBox: Displays a warning message if all selected variables are of type "String".
    """
    
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
    """
    Assigns auxiliary variables from the selected indexes in the parent's variables list.
    This function performs the following steps:
    1. Retrieves the selected indexes from the parent's variables list.
    2. Filters out non-numeric variables from the selected indexes.
    3. If no valid numeric variables are selected, displays a warning message.
    4. Adds the new numeric variables to the parent's auxiliary variables list.
    5. Updates the parent's auxiliary model with the new list of auxiliary variables.
    6. Removes the selected variables from the parent's variables list.
    7. Calls the show_r_script function to update the R script.
    Args:
        parent: The parent object containing the variables list, auxiliary variables list, and auxiliary model.
    """
    
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
    """
    Assigns a variable directory (vardir) from the selected variables in the parent object's variables list.
    This function checks the selected variables in the parent object's variables list. If any of the selected 
    variables are not of type "String", it assigns the first non-string variable to the vardir_var attribute 
    of the parent object, updates the vardir_model with this variable, removes the variable from the variables 
    list, and calls the show_r_script function. If all selected variables are of type "String", it displays a 
    warning message indicating that the vardir variable must be of type Numeric.
    Args:
        parent: The parent object containing the variables list, vardir_var, and vardir_model attributes.
    Raises:
        None
    Displays:
        QMessageBox: A warning message if all selected variables are of type "String".
    """
    
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
    """
    Assigns selected variables as factors (only variables of type String) and updates the parent object's factor variable list and model.
    Args:
        parent: An object that contains the following attributes:
            - variables_list: A QListView or similar widget that holds the list of variables.
            - as_factor_var: A list that stores the variables to be treated as factors.
            - as_factor_model: A QStringListModel or similar model that represents the factor variables.
    The function performs the following steps:
        1. Retrieves the selected indexes from the variables_list.
        2. Filters only variables of type "String".
        3. Adds them to the as_factor_var list, ensuring no duplicates.
        4. Updates the as_factor_model with the new list of factor variables.
        5. Removes the selected variables from the variables_list.
        6. Calls the show_r_script function to update the R script display.
    """

    selected_indexes = parent.variables_list.selectedIndexes()
    if selected_indexes:
        new_vars = []
        rows_to_remove = []
        for index in selected_indexes:
            type_of_var = index.data().split(" [")[1].replace("]", "")
            if type_of_var == "String":
                new_vars.append(index.data())
                rows_to_remove.append(index.row())
        if not new_vars:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText("No valid string variables selected. Please select at least one variable of type String.")
            msg.setWindowTitle("Warning")
            msg.exec()
            return
        parent.as_factor_var = list(set(parent.as_factor_var + new_vars))
        parent.as_factor_model.setStringList(parent.as_factor_var)
        for row in sorted(rows_to_remove, reverse=True):
            parent.variables_list.model().removeRow(row)
        show_r_script(parent)

def unassign_variable(parent):
    """
    Unassigns selected variables from the specified lists in the parent object and adds them back to the variables list.
    This function checks for selected items in the following lists in order:
    1. of_interest_list
    2. auxilary_list
    3. vardir_list
    4. as_factor_list
    For each list, if there are selected items, it removes these items from the corresponding variable list in the parent object,
    updates the model for that list, and adds the items back to the variables list. It then calls the show_r_script function.
    Args:
        parent: The parent object containing the lists and models to be updated.
    """
    
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
    """
    Retrieve selected variables from the parent object.
    Args:
        parent (object): The parent object containing the variables of interest.
    Returns:
        tuple: A tuple containing the following variables from the parent object:
            - of_interest_var: The variable of interest.
            - auxilary_vars: Auxiliary variables.
            - vardir_var: The variable direction.
            - as_factor_var: The factor variable.
    """
    
    return parent.of_interest_var, parent.auxilary_vars, parent.vardir_var, parent.as_factor_var

def generate_r_script(parent):
    """
    Generates an R script based on the provided parent object's attributes.
    Args:
        parent (object): An object containing the following attributes:
            - of_interest_var (list): A list containing the variable of interest.
            - auxilary_vars (list): A list of auxiliary variables.
            - vardir_var (list): A list containing the variance directory variable.
            - as_factor_var (list): A list of variables to be treated as factors.
            - selection_method (str): The method for variable selection (e.g., "Stepwise", "None").
            - model_method (str): The method for modeling (e.g., "lm", "glm").
            - iter_update (int): The number of iterations for updating the model.
            - iter_mcmc (int): The number of MCMC iterations.
            - burn_in (int): The number of burn-in iterations.
    Returns:
        str: The generated R script as a string.
    """
    
    of_interest_var = f'{parent.of_interest_var[0].split(" [")[0].replace(" ", "_")}' if parent.of_interest_var else '""'
    auxilary_vars = " + ".join([var.split(" [")[0].replace(" ", "_") for var in parent.auxilary_vars]) if parent.auxilary_vars else '""'
    vardir_var = f'{parent.vardir_var[0].split(" [")[0].replace(" ", "_")}' if parent.vardir_var else '""'
    
    dummy_vars = []
    dummy_creation_script = ""
    if parent.as_factor_var:
        for var in parent.as_factor_var:
            var_name = var.split(" [")[0].replace(" ", "_")
            dummy_creation_script += f'dummies_{var_name} <- model.matrix(~{var_name} - 1, data)\n'
            dummy_creation_script += f'data <- cbind(data, dummies_{var_name})\n'
            dummy_vars.append(f'colnames(dummies_{var_name})')

    # Gabungkan semua dummy variable ke formula
    dummy_vars_str = ""
    if dummy_vars:
        dummy_names = []
        for var in parent.as_factor_var:
            var_name = var.split(" [")[0].replace(" ", "_")
            # You don't know the levels in Python, so use a placeholder for R to expand
            dummy_names.append(f'colnames(dummies_{var_name})')
        # Instead of using paste() in formula, expand in R before formula creation
        dummy_vars_str = " + ".join([f'`{name}`' for name in dummy_names])
    
    
    r_script = f'names(data) <- gsub(" ", "_", names(data)); #Replace space with underscore\n'
    r_script += dummy_creation_script

    # Build the formula in R after dummies are created
    r_script += "all_vars <- names(data)\n"
    if parent.as_factor_var:
        for var in parent.as_factor_var:
            var_name = var.split(" [")[0].replace(" ", "_")
            r_script += f'all_vars <- c(all_vars, colnames(dummies_{var_name}))\n'

    # Build the formula string in R
    r_script += "rhs_vars <- c()"
    if auxilary_vars != '""':
        r_script += f'\nrhs_vars <- c(rhs_vars, "{auxilary_vars}")'
    if parent.as_factor_var:
        for var in parent.as_factor_var:
            var_name = var.split(" [")[0].replace(" ", "_")
            r_script += f'\nrhs_vars <- c(rhs_vars, colnames(dummies_{var_name}))'
    r_script += '\nformula_str <- paste('
    if of_interest_var != '""':
        r_script += f'"{of_interest_var}", "~", paste(rhs_vars, collapse = " + "))\n'
    else:
        r_script += '"", "~", paste(rhs_vars, collapse = " + "))\n'
    r_script += "formula <- as.formula(formula_str)\n"
    
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
    """
    Generates an R script using the given parent object and sets the text of the parent's R script editor.
    Args:
        parent: An object that contains the method `generate_r_script` and the attribute `r_script_edit`.
                The `generate_r_script` method is used to generate the R script, and `r_script_edit` is
                an editor widget where the generated R script will be displayed.
    """
    
    r_script = generate_r_script(parent)
    parent.r_script_edit.setText(r_script)

def get_script(parent):
    """
    Retrieves the text content from the 'r_script_edit' attribute of the given parent object.
    Args:
        parent: An object that contains an attribute 'r_script_edit' which is expected to be a QTextEdit or similar widget.
    Returns:
        str: The text content of the 'r_script_edit' widget as a plain string.
    """
    
    return parent.r_script_edit.toPlainText()  

def show_options(parent):
    """
    Displays a dialog window with options for configuring the stepwise selection method and iteration parameters.
    Parameters:
    parent (QWidget): The parent widget for the dialog.
    The dialog includes the following options:
    - Number of Iteration Update (minimum 2): A QLineEdit for specifying the number of iteration updates, with a default value of 3.
    - Number of Total Iterations per Chain: A QLineEdit for specifying the total number of iterations per chain, with a default value of 2000.
    - Number of iterations to discard at the beginning: A QLineEdit for specifying the number of iterations to discard at the beginning, with a default value of 1000.
    The dialog also includes "OK" and "Cancel" buttons. Clicking "OK" will apply the settings and close the dialog, while clicking "Cancel" will close the dialog without applying any changes.
    """
    
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
    """
    Sets the selection method and updates iteration parameters for the parent object,
    then accepts the dialog and shows the R script.
    Args:
        parent: The parent object containing the selection method and iteration parameters.
        dialog: The dialog object to be accepted.
    Side Effects:
        Updates the following attributes of the parent object:
        - iter_update: The updated iteration value.
        - iter_mcmc: The updated MCMC iteration value.
        - burn_in: The updated burn-in value.
        Accepts the dialog and calls the show_r_script function with the parent object.
    """
    
    # parent.selection_method = parent.method_combo.currentText()
    parent.iter_update = parent.iter_update.text()
    parent.iter_mcmc = parent.iter_mcmc.text()
    parent.burn_in = parent.burn_in.text()
    dialog.accept()
    show_r_script(parent)