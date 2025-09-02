from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QComboBox, QLineEdit
from PyQt6.QtGui import QIntValidator
from PyQt6.QtWidgets import QMessageBox

def assign_of_interest(parent):
    """
    Assigns a variable of interest from the selected indexes in the variables list.
    This function checks the selected indexes in the `variables_list` of the `parent` object.
    If any of the selected variables is not of type "String", it assigns that variable as the
    variable of interest, updates the `of_interest_model` with this variable, removes the variable
    from the `variables_list`, and calls the `show_r_script` function. If all selected variables
    are of type "String", it shows a warning message indicating that the variable of interest must
    be of type Numeric.
    Args:
        parent: The parent object containing the `variables_list`, `of_interest_var`, `of_interest_model`,
                and the `show_r_script` function.
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
                old_var = parent.of_interest_var[0] if parent.of_interest_var else None
                parent.of_interest_var = [index.data()]
                parent.of_interest_model.setStringList(parent.of_interest_var)
                parent.variables_list.model().removeRow(selected_indexes[-1].row())  # Remove from variables list
                if old_var:
                    parent.variables_list.model().insertRow(0)
                    parent.variables_list.model().setData(parent.variables_list.model().index(0), old_var)
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
    Assigns auxiliary variables from the selected indexes in the parent object's variables list.
    This function performs the following steps:
    1. Retrieves the selected indexes from the parent object's variables list.
    2. Filters out non-numeric variables from the selected indexes.
    3. If no valid numeric variables are selected, displays a warning message and exits.
    4. Adds the new numeric variables to the parent object's auxiliary variables list.
    5. Updates the auxiliary model with the new list of auxiliary variables.
    6. Removes the selected variables from the parent object's variables list.
    7. Calls the show_r_script function with the parent object.
    Args:
        parent (object): The parent object containing the variables list, auxiliary variables list, and auxiliary model.
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

def assign_index(parent):
    """
    Assigns the selected index from the variables list to the parent's index variable and updates the index model.
    Parameters:
    parent (object): The parent object that contains the variables list, index variable, and index model.
    The function performs the following steps:
    1. Retrieves the selected indexes from the parent's variables list.
    2. If there are selected indexes, it iterates through them.
    3. Assigns the data of the first selected index to the parent's index variable.
    4. Updates the parent's index model with the new index variable.
    5. Removes the selected index from the variables list.
    6. Calls the show_r_script function with the parent object.
    7. Breaks the loop after processing the first selected index.
    """
    
    selected_indexes = parent.variables_list.selectedIndexes()
    if selected_indexes:
        for index in selected_indexes:
            old_var = parent.index_var[0] if parent.index_var else None
            parent.index_var = [index.data()]
            parent.index_model.setStringList(parent.index_var)
            parent.variables_list.model().removeRow(selected_indexes[-1].row())  # Remove from variables list
            if old_var:
                parent.variables_list.model().insertRow(0)
                parent.variables_list.model().setData(parent.variables_list.model().index(0), old_var)
            show_r_script(parent)
            break

def assign_as_factor(parent):
    """
    Assigns selected variables as factors and updates the parent object's factor list and model.
    Args:
        parent: An object that contains the following attributes:
            - variables_list: A QListView or similar object with a method selectedIndexes() that returns a list of selected indexes.
            - as_factor_var: A list of variables that are currently assigned as factors.
            - as_factor_model: A QStringListModel or similar object with a method setStringList() to update the list of factor variables.
    The function performs the following steps:
        1. Retrieves the selected indexes from the variables_list.
        2. Extracts the data from each selected index and appends it to a new list of variables.
        3. Updates the as_factor_var list by adding new variables, ensuring no duplicates.
        4. Updates the as_factor_model with the new list of factor variables.
        5. Removes the selected variables from the variables_list.
        6. Calls the show_r_script function to update the R script display.
    """
    
    selected_indexes = parent.variables_list.selectedIndexes()
    if selected_indexes:
        old_var = parent.as_factor_var[0] if parent.as_factor_var else None
        last_index = selected_indexes[-1]  # Get the last selected index
        new_var = last_index.data()  # Get the data of the last selected variable
        parent.as_factor_var = [new_var]  # Assign only the last variable
        parent.as_factor_model.setStringList(parent.as_factor_var)
        parent.variables_list.model().removeRow(last_index.row())  # Remove the last selected variable from the list
        if old_var:
            parent.variables_list.model().insertRow(0)
            parent.variables_list.model().setData(parent.variables_list.model().index(0), old_var)
        show_r_script(parent)
        
def assign_domains(parent):
    """
    Assigns the selected domain variable from the variables list to the domain model of the parent object.
    Parameters:
    parent (object): The parent object that contains the variables list and domain model.
    The function performs the following steps:
    1. Retrieves the selected indexes from the parent's variables list.
    2. If there are selected indexes, it assigns the first selected variable to the parent's domain variable.
    3. Updates the parent's domain model with the selected domain variable.
    4. Removes the selected variable from the parent's variables list.
    5. Calls the show_r_script function with the parent object as an argument.
    """
    
    selected_indexes = parent.variables_list.selectedIndexes()
    if selected_indexes:
        old_var = parent.domain_var[0] if parent.domain_var else None
        parent.domain_var = [selected_indexes[0].data()]  # Only one variable
        parent.domain_model.setStringList(parent.domain_var)
        parent.variables_list.model().removeRow(selected_indexes[0].row())  # Remove from variables list
        if old_var:
            parent.variables_list.model().insertRow(0)
            parent.variables_list.model().setData(parent.variables_list.model().index(0), old_var)
        show_r_script(parent)

def assign_aux_mean(parent):
    """
    Assigns auxiliary mean variables from the selected indexes in the parent object's variables list.
    This function performs the following steps:
    1. Retrieves the selected indexes from the parent object's variables list.
    2. Filters out non-numeric variables from the selected indexes.
    3. If no valid numeric variables are selected, displays a warning message.
    4. Adds the new numeric variables to the parent object's auxiliary mean variables list.
    5. Updates the auxiliary mean model with the new list of variables.
    6. Removes the selected variables from the parent object's variables list.
    7. Calls the show_r_script function to update the R script display.
    Args:
        parent: The parent object containing the variables list, auxiliary mean variables list, 
                and auxiliary mean model.
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
        parent.aux_mean_vars = list(set(parent.aux_mean_vars + new_vars))  # Add new variables if they are different
        parent.aux_mean_model.setStringList(parent.aux_mean_vars)
        for index in sorted(selected_indexes, reverse=True):
            parent.variables_list.model().removeRow(index.row())  # Remove from variables list
        show_r_script(parent)

def assign_population_sample_size(parent):
    """
    Assigns the population sample size based on the selected index from the variables list.
    Args:
        parent: The parent object that contains the variables list and other related attributes.
    This function performs the following steps:
    1. Retrieves the selected indexes from the parent's variables list.
    2. If there are selected indexes, it assigns the first selected index's data to the parent's population_sample_size_var.
    3. Updates the parent's population_sample_size_model with the new population sample size.
    4. Removes the selected index from the variables list.
    5. Calls the show_r_script function with the parent object.
    """
    
    selected_indexes = parent.variables_list.selectedIndexes()
    if selected_indexes:
        old_var = parent.population_sample_size_var[0] if parent.population_sample_size_var else None
        parent.population_sample_size_var = [selected_indexes[0].data()]  # Only one variable
        parent.population_sample_size_model.setStringList(parent.population_sample_size_var)
        parent.variables_list.model().removeRow(selected_indexes[0].row())  # Remove from variables list
        if old_var:
            parent.variables_list.model().insertRow(0)
            parent.variables_list.model().setData(parent.variables_list.model().index(0), old_var)
        show_r_script(parent)

def unassign_variable(parent):
    """
    Unassigns selected variables from various lists in the parent object and adds them back to the main variables list.
    This function checks for selected items in several lists within the parent object, removes the selected items from
    their respective lists, and then adds them back to the main variables list. It also updates the corresponding models
    and triggers the `show_r_script` function to reflect the changes.
    Args:
        parent: The parent object containing the lists and models. It is expected to have the following attributes:
            - of_interest_list
            - of_interest_var
            - of_interest_model
            - auxilary_list
            - auxilary_vars
            - auxilary_model
            - index_list
            - index_var
            - index_model
            - as_factor_list
            - as_factor_var
            - as_factor_model
            - domain_list
            - domain_var
            - domain_model
            - auxilary_vars_mean_list
            - aux_mean_vars
            - aux_mean_model
            - population_sample_size_list
            - population_sample_size_var
            - population_sample_size_model
            - variables_list
    Returns:
        None
    """
    
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

    selected_indexes = parent.auxilary_vars_mean_list.selectedIndexes()
    if selected_indexes:
        selected_items = [index.data() for index in selected_indexes]
        parent.aux_mean_vars = [var for var in parent.aux_mean_vars if var not in selected_items]
        parent.aux_mean_model.setStringList(parent.aux_mean_vars)
        for item in selected_items:
            parent.variables_list.model().insertRow(0)  # Add back to variables list
            parent.variables_list.model().setData(parent.variables_list.model().index(0), item)
        show_r_script(parent)
        return

    selected_indexes = parent.population_sample_size_list.selectedIndexes()
    if selected_indexes:
        selected_items = [index.data() for index in selected_indexes]
        parent.population_sample_size_var = [var for var in parent.population_sample_size_var if var not in selected_items]
        parent.population_sample_size_model.setStringList(parent.population_sample_size_var)
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
        tuple: A tuple containing the following elements:
            - of_interest_var: The variable of interest.
            - auxilary_vars: The auxiliary variables.
            - vardir_var: The variable directory.
            - as_factor_var: The factor variable.
    """
    
    return parent.of_interest_var, parent.auxilary_vars, parent.vardir_var, parent.as_factor_var

def generate_r_script(parent):
    """
    Generates an R script for statistical modeling based on the provided parent object.
    Args:
        parent (object): An object containing the following attributes:
            - of_interest_var (list): A list containing the variable of interest.
            - auxilary_vars (list): A list of auxiliary variables.
            - as_factor_var (list): A list of variables to be treated as factors.
            - index_var (list): A list containing the index variable.
            - aux_mean_vars (list): A list of auxiliary mean variables.
            - population_sample_size_var (list): A list containing the population sample size variable.
            - domain_var (list): A list containing the domain variable.
            - selection_method (str): The method for variable selection (e.g., "Stepwise", "None").
            - bootstrap (int): The number of bootstrap samples.
            - method (str): The method to be used in the pbmseBHF function.
    Returns:
        str: The generated R script as a string.
    """
    
    of_interest_var = f'{parent.of_interest_var[0].split(" [")[0].replace(" ", "_")}' if parent.of_interest_var else '""'
    auxilary_vars = " + ".join([var.split(" [")[0].replace(" ", "_") for var in parent.auxilary_vars]) if parent.auxilary_vars else '""'
    as_factor_var = " + ".join([f'as.factor({var.split(" [")[0].replace(" ", "_")})' for var in parent.as_factor_var]) if parent.as_factor_var else '""'
    index_var = f'{parent.index_var[0].split(" [")[0].replace(" ", "_")}' if parent.index_var else '""'
    aux_mean_vars = ",".join([f'{var.split(" [")[0].replace(" ", "_")}' for var in parent.aux_mean_vars]) if parent.aux_mean_vars else '""'
    domain_var = f'{parent.domain_var[0].split(" [")[0].replace(" ", "_")}' if parent.domain_var else '""'
    
    if (auxilary_vars=='""' or auxilary_vars is None) and as_factor_var=='""':
        formula = f'{of_interest_var} ~ 1'
    elif as_factor_var=='""':
        formula = f'{of_interest_var} ~ {auxilary_vars}'
    elif auxilary_vars=='""':
        formula = f'{of_interest_var} ~ {as_factor_var}'
    else:
        formula = f'{of_interest_var} ~ {auxilary_vars} + {as_factor_var}'

    r_script = f'names(datahb_unit) <- gsub(" ", "_", names(datahb_unit)); #Replace space with underscore\n'
    r_script += f'formula <- {formula}\n'
    r_script += f'Xmeans <- with(datahb_unit, data.frame({index_var},{aux_mean_vars}))\n'
    r_script += f'Xmeans <- na.omit(Xmeans)\n'
    r_script += f'Xmeans <- Xmeans[complete.cases(Xmeans), ]\n'
    if index_var != domain_var and index_var != '""' and domain_var != '""':
        r_script += f'Xmeans${domain_var} <- Xmeans${index_var}\n'
    
    if parent.selection_method=="Stepwise":
        parent.selection_method = "both"
    if parent.selection_method and parent.selection_method != "None" and auxilary_vars:
        r_script += f'stepwise_model <- step(formula, direction="{parent.selection_method.lower()}")\n'
        r_script += f'final_formula <- formula(stepwise_model)\n'
        r_script += f'model_unit<-hb_unit(final_formula, data_unit = datahb_unit, data_area= Xmeans,domain="{domain_var}", iter.update={parent.iter_update}, iter.mcmc = {parent.iter_mcmc}, burn.in = {parent.burn_in}, thin = {parent.thin})'
    else:
        r_script += f'model_unit<-hb_unit(formula, data_unit = datahb_unit, data_area= Xmeans,domain="{domain_var}", iter.update={parent.iter_update}, iter.mcmc = {parent.iter_mcmc}, burn.in = {parent.burn_in}, thin = {parent.thin})'
    return r_script

def show_r_script(parent):
    """
    Generates an R script using the given parent object and sets the text of the parent's r_script_edit widget to the generated script.
    Args:
        parent: The parent object that contains the r_script_edit widget and is used to generate the R script.
    """
    
    r_script = generate_r_script(parent)
    parent.r_script_edit.setText(r_script)

def get_script_hb(parent):
    """
    Retrieves the text content from the r_script_edit attribute of the parent object.
    Args:
        parent: An object that contains an attribute r_script_edit, which is expected to have a method toPlainText().
    Returns:
        str: The text content of the r_script_edit attribute.
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
    iter_update_label = QLabel("Number of Iteration Update (minimum 2):")
    layout.addWidget(iter_update_label)
    
    parent.iter_update = QLineEdit()
    parent.iter_update.setValidator(QIntValidator())
    parent.iter_update.setText("3")  # Set default value to 3
    layout.addWidget(parent.iter_update)
    
    iter_mcmc_label = QLabel("Number of MCMC:")
    layout.addWidget(iter_mcmc_label)
    
    parent.iter_mcmc = QLineEdit()
    parent.iter_mcmc.setValidator(QIntValidator())
    parent.iter_mcmc.setText("10000")
    layout.addWidget(parent.iter_mcmc)
    
    burn_in_label = QLabel("Burn in:")
    layout.addWidget(burn_in_label)
    
    parent.burn_in = QLineEdit()
    parent.burn_in.setValidator(QIntValidator())
    parent.burn_in.setText("2000")  # Set default value to 2000
    layout.addWidget(parent.burn_in)

    thin_label = QLabel("Thin:")
    layout.addWidget(thin_label)

    parent.thin = QLineEdit()
    parent.thin.setValidator(QIntValidator())
    parent.thin.setText("2")  # Set default value to 2
    layout.addWidget(parent.thin)

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
    parent.thin = parent.thin.text()
    dialog.accept()
    show_r_script(parent)