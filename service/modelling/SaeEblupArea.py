from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QComboBox
from PyQt6.QtWidgets import QMessageBox

def assign_of_interest(parent):
    """
    Assigns the variable of interest from the selected indexes in the variables list.
    This function checks the selected indexes in the `variables_list` of the `parent` object.
    If any of the selected variables is not of type "String", it assigns that variable as the 
    variable of interest (`of_interest_var`) and updates the `of_interest_model` with this variable.
    It also removes the selected variable from the `variables_list` and calls the `show_r_script` function.
    If all selected variables are of type "String", it shows a warning message indicating that 
    the variable of interest must be of type Numeric.
    Args:
        parent (object): The parent object containing the `variables_list`, `of_interest_var`, 
                         `of_interest_model`, and other related attributes.
    Raises:
        None
    Returns:
        None
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
    Assigns auxiliary variables from the selected indexes in the parent's variables list to the parent's auxiliary variables list.
    Parameters:
    parent (object): The parent object containing the variables list and auxiliary variables list.
    The function performs the following steps:
    1. Retrieves the selected indexes from the parent's variables list.
    2. Filters out non-numeric variables from the selected indexes.
    3. If no valid numeric variables are selected, displays a warning message and exits the function.
    4. Adds the new numeric variables to the parent's auxiliary variables list, ensuring no duplicates.
    5. Updates the parent's auxiliary model with the new list of auxiliary variables.
    6. Removes the selected variables from the parent's variables list.
    7. Calls the `show_r_script` function to update the R script display.
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
    Parameters:
    parent (object): The parent object containing the variables list and vardir attributes.
    Functionality:
    - Checks the selected indexes in the parent's variables list.
    - If there are selected indexes, it iterates through them to determine the type of each variable.
    - If a variable is not of type "String", it assigns it to the parent's vardir_var attribute and updates the vardir_model.
    - Removes the selected variable from the variables list.
    - Calls the show_r_script function with the parent object.
    - If all selected variables are of type "String", displays a warning message indicating that the vardir variable must be of type Numeric.
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
    Assigns selected variables as factors and updates the parent object's factor list and model.
    Args:
        parent: An object that contains the following attributes:
            - variables_list: A QListView or similar object with a method selectedIndexes() 
              that returns a list of selected indexes.
            - as_factor_var: A list of variables that are currently assigned as factors.
            - as_factor_model: A QStringListModel or similar object with a method setStringList() 
              that updates the model with a new list of factor variables.
    The function performs the following steps:
        1. Retrieves the selected indexes from the variables_list.
        2. Extracts the data from each selected index and appends it to a new list of variables.
        3. Updates the as_factor_var list with the new variables, ensuring no duplicates.
        4. Updates the as_factor_model with the new list of factor variables.
        5. Removes the selected variables from the variables_list.
        6. Calls the show_r_script function with the parent object as an argument.
    """
    
    selected_indexes = parent.variables_list.selectedIndexes()
    if selected_indexes:
        last_index = selected_indexes[-1]  # Get the last selected index
        new_var = last_index.data()  # Get the data of the last selected variable
        parent.as_factor_var = [new_var]  # Assign only the last variable
        parent.as_factor_model.setStringList(parent.as_factor_var)
        parent.variables_list.model().removeRow(last_index.row())  # Remove the last selected variable from the list
        show_r_script(parent)

def unassign_variable(parent):
    """
    Unassigns selected variables from various lists in the parent object and adds them back to the variables list.
    This function checks for selected items in the following lists of the parent object:
    - of_interest_list
    - auxilary_list
    - vardir_list
    - as_factor_list
    For each list, if there are selected items, it removes these items from the corresponding variable list in the parent object,
    updates the model for that list, and adds the items back to the variables list. Finally, it calls the `show_r_script` function
    to update the R script display.
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
    Parameters:
    parent (object): An object that contains the variables of interest.
    Returns:
    tuple: A tuple containing the following variables from the parent object:
        - of_interest_var: The variable of interest.
        - auxilary_vars: Auxiliary variables.
        - vardir_var: Variance direction variable.
        - as_factor_var: Factor variable.
    """
    
    return parent.of_interest_var, parent.auxilary_vars, parent.vardir_var, parent.as_factor_var

def generate_r_script(parent):
    """
    Generates an R script for model fitting based on the provided parent object.
    Args:
        parent (object): An object containing the following attributes:
            - of_interest_var (list): A list containing the variable of interest.
            - auxilary_vars (list): A list of auxiliary variables.
            - vardir_var (list): A list containing the variance directory variable.
            - as_factor_var (list): A list of variables to be treated as factors.
            - selection_method (str): The method for variable selection ("Stepwise", "None", or other).
            - method (str): The method to be used in the mseFH function.
    Returns:
        str: The generated R script as a string.
    """
    
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
        r_script += f'model<-mseFH(final_formula, {vardir_var}, method = "{parent.method}", data=data)'
    else:
        r_script += f'model<-mseFH(formula, {vardir_var}, method = "{parent.method}", data=data)'
    return r_script

def show_r_script(parent):
    """
    Generates an R script using the provided parent object and sets the text of the parent's R script editor.
    Args:
        parent: An object that contains the method `generate_r_script` and the attribute `r_script_edit`.
                The `generate_r_script` method is used to generate the R script, and the `r_script_edit` attribute
                is expected to have a `setText` method to update the editor's text.
    Returns:
        None
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
    Displays a dialog window with options for selecting a method.
    Parameters:
    parent (QWidget): The parent widget to which this dialog belongs.
    The dialog contains a combo box for selecting a method from the options 
    "ML", "REML", and "FH", with "REML" set as the default selection. 
    It also includes "OK" and "Cancel" buttons. The "OK" button triggers 
    the set_selection_method function, while the "Cancel" button closes the dialog.
    """
    
    options_dialog = QDialog(parent)
    options_dialog.setWindowTitle("Options")

    layout = QVBoxLayout()

    # method_label = QLabel("Stepwise Selection Method:")
    # layout.addWidget(method_label)

    # parent.method_combo = QComboBox()
    # parent.method_combo.addItems(["None", "Stepwise", "Forward", "Backward"])
    # layout.addWidget(parent.method_combo)

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
    """
    Sets the selection method for the parent object and accepts the dialog.
    This function retrieves the current text from the method selection combo box
    of the parent object and assigns it to the parent's method attribute. It then
    accepts the dialog and calls the show_r_script function with the parent object
    as an argument.
    Args:
        parent: The parent object that contains the method selection combo box.
        dialog: The dialog object that will be accepted.
    Returns:
        None
    """
    
    # parent.selection_method = parent.method_combo.currentText()
    parent.method = parent.method_selection.currentText()
    dialog.accept()
    show_r_script(parent)