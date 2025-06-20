from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QComboBox, QLineEdit
from PyQt6.QtGui import QDoubleValidator, QIntValidator
from PyQt6.QtWidgets import QMessageBox


def assign_of_interest(parent):
    """
    Assigns the variable of interest from the selected indexes in the variables list.
    This function checks the selected variables in the `variables_list` of the `parent` object.
    If the selected variable is of type "String" and the projection method is "Linear", it shows a warning message.
    Otherwise, it assigns the selected variable as the variable of interest, updates the `of_interest_model`,
    removes the variable from the `variables_list`, and calls the `show_r_script` function.
    Args:
        parent: The parent object containing the variables list, projection method, and other related attributes.
    Raises:
        QMessageBox: Displays a warning message if all selected variables are of type "String" and the projection method is "Linear".
    """
    
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
    """
    Assigns selected auxiliary variables from the parent object's variables list to its auxiliary variables list.
    Parameters:
    parent (object): The parent object containing the variables list and auxiliary variables list.
    Functionality:
    - Retrieves the selected indexes from the parent's variables list.
    - Filters out non-numeric variables from the selected indexes.
    - If no valid numeric variables are selected, displays a warning message.
    - Adds the new numeric variables to the parent's auxiliary variables list, ensuring no duplicates.
    - Updates the parent's auxiliary model with the new list of auxiliary variables.
    - Removes the selected variables from the parent's variables list.
    - Calls the show_r_script function with the parent object.
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
    Assigns the selected index from the variables list to the index variable of the parent object,
    updates the index model with the new index, removes the selected index from the variables list,
    and calls the show_r_script function.
    Args:
        parent: An object that contains the following attributes:
            - variables_list: A QListView or similar widget that holds the list of variables.
            - index_var: A list to store the selected index data.
            - index_model: A QStringListModel or similar model to update with the new index.
    Returns:
        None
    """
    
    selected_indexes = parent.variables_list.selectedIndexes()
    if selected_indexes:
        for index in selected_indexes:
            parent.index_var = [index.data()]
            parent.index_model.setStringList(parent.index_var)
            parent.variables_list.model().removeRow(selected_indexes[-1].row())  # Remove from variables list
            show_r_script(parent)
            break

def assign_as_factor(parent):
    """
    Assigns selected variables as factors and updates the parent object's factor list and model.
    Args:
        parent: The parent object containing the variables list and factor list.
    The function performs the following steps:
    1. Retrieves the selected indexes from the parent's variables list.
    2. Extracts the data from the selected indexes and adds them to a new list of variables.
    3. Updates the parent's factor variable list by adding new variables if they are not already present.
    4. Updates the parent's factor model with the new factor variable list.
    5. Removes the selected variables from the parent's variables list.
    6. Calls the `show_r_script` function to update the R script display.
    """
    
    selected_indexes = parent.variables_list.selectedIndexes()
    if selected_indexes:
        last_index = selected_indexes[-1]  # Get the last selected index
        new_var = last_index.data()  # Get the data of the last selected variable
        parent.as_factor_var = [new_var]  # Assign only the last variable
        parent.as_factor_model.setStringList(parent.as_factor_var)
        parent.variables_list.model().removeRow(last_index.row())  # Remove the last selected variable from the list
        show_r_script(parent)
        
def assign_domains(parent):
    """
    Assigns the selected domain variable from the variables list to the domain model.
    Parameters:
    parent (object): The parent object containing the variables list and domain model.
    The function performs the following steps:
    1. Retrieves the selected indexes from the parent's variables list.
    2. If there are selected indexes, assigns the first selected variable to the parent's domain variable.
    3. Updates the parent's domain model with the selected domain variable.
    4. Removes the selected variable from the parent's variables list.
    5. Calls the show_r_script function with the parent object.
    """
    
    selected_indexes = parent.variables_list.selectedIndexes()
    if selected_indexes:
        parent.domain_var = [selected_indexes[0].data()]  # Only one variable
        parent.domain_model.setStringList(parent.domain_var)
        parent.variables_list.model().removeRow(selected_indexes[0].row())  # Remove from variables list
        show_r_script(parent)
        
def assign_weight(parent):
    """
    Assigns a weight variable from the selected indexes in the variables list.
    Parameters:
    parent (object): The parent object containing the variables list and weight model.
    Behavior:
    - Checks the selected indexes in the variables list.
    - If any selected variable is not of type "String", assigns it as the weight variable.
    - Updates the weight model with the selected weight variable.
    - Removes the selected weight variable from the variables list.
    - Calls the show_r_script function with the parent object.
    - If all selected variables are of type "String", displays a warning message indicating that the weight variable must be of type Numeric.
    """
    
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
    """
    Assigns a selected variable to the strata list and updates the UI components accordingly.
    Args:
        parent: The parent object that contains the UI components and variables list.
    The function performs the following steps:
    1. Retrieves the selected indexes from the variables list.
    2. If there are selected indexes, it assigns the first selected variable to the strata list.
    3. Updates the strata model with the new strata variable.
    4. Removes the selected variable from the variables list.
    5. Calls the show_r_script function to update the R script display.
    """
    
    selected_indexes = parent.variables_list.selectedIndexes()
    if selected_indexes:
        parent.strata_var = [selected_indexes[0].data()]  # Only one variable
        parent.strata_model.setStringList(parent.strata_var)
        parent.variables_list.model().removeRow(selected_indexes[0].row())  # Remove from variables list
        show_r_script(parent)

def unassign_variable(parent):
    """
    Unassigns selected variables from various lists in the parent object and adds them back to the variables list.
    This function checks for selected indexes in the following lists in order:
    - of_interest_list
    - auxilary_list
    - index_list
    - as_factor_list
    - domain_list
    - strata_list
    - weight_list
    For each list, if there are selected items, it removes the selected items from the corresponding variable list in the parent object,
    updates the model for that list, and adds the items back to the variables list. Finally, it calls the show_r_script function.
    Args:
        parent: The parent object containing the lists and models to be updated.
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
    """
    Retrieve selected variables from the given parent object.
    Args:
        parent (object): An object containing the variables of interest.
    Returns:
        tuple: A tuple containing the following variables from the parent object:
            - of_interest_var: The primary variable of interest.
            - auxilary_vars: Auxiliary variables related to the primary variable.
            - vardir_var: Directional variable.
            - as_factor_var: Factor variable.
    """
    
    return parent.of_interest_var, parent.auxilary_vars, parent.vardir_var, parent.as_factor_var

def process_vars(vars_list, prefix, suffix):
    """
    Processes a list of variable names by modifying them with a given prefix and suffix,
    and generates R script lines to assign these modified variable names to data columns.
    Args:
        vars_list (list of str): List of variable names to be processed.
        prefix (str): Prefix to be added to each variable name.
        suffix (str): Suffix to be added to each variable name.
    Returns:
        None
    """
    
    for var in vars_list:
        var_name = var.split(" [")[0].replace(" ", "_")
        var_name_edit = f"{prefix}{var_name}{suffix}"
        r_script += f'{var_name} <- data["{var_name_edit}"];\n'

def generate_r_script(parent):
    """
    Generates an R script based on the provided parent object.
    Args:
        parent: An object containing the following attributes:
            - of_interest_var: List of variables of interest.
            - auxilary_vars: List of auxiliary variables.
            - as_factor_var: List of variables to be treated as factors.
            - index_var: List of index variables.
            - domain_var: List of domain variables.
            - weight_var: List of weight variables.
            - strata_var: List of strata variables.
            - projection_method: String specifying the projection method (e.g., "Linear", "Logistic", "SVM Linear", "SVM RBF", "Neural Network", "Gradient Boost").
            - epoch: Integer specifying the number of epochs (used for Neural Network).
            - learning_rate: Float specifying the learning rate (used for Neural Network).
            - var_position: String specifying the position of variables ("After" or "Before").
            - model_name: String specifying the model name.
            - separator: String specifying the separator to be used.
            - projection_name: String specifying the projection name.
            - selection_method: String specifying the selection method (e.g., "Stepwise", "None").
            - metric: String specifying the model metric.
            - k_fold: Integer specifying the number of folds for cross-validation.
            - grid: Grid specification for tuning parameters.
    Returns:
        str: The generated R script as a string.
    """
    
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
        "Neural Network": f"mlp(mode='classification', engine='nnet', epochs={parent.epoch}, learn_rate={parent.learning_rate})"
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
                r_script += f'{var.split(" [")[0].replace(" ", "_")} <- as.factor(data_pe[["{var_name_edit}"]]);\n'
            else:
                r_script += f'{var.split(" [")[0].replace(" ", "_")} <- data_pe[["{var_name_edit}"]];\n'
        
        for var in parent.auxilary_vars:
            var_name_edit = format_edit_var(var, parent.model_name + parent.separator)
            r_script += f'{var.split(" [")[0].replace(" ", "_")} <- data_pe[["{var_name_edit}"]];\n'
        
        for var in parent.as_factor_var:
            var_name_edit = format_edit_var(var, parent.model_name + parent.separator)
            r_script += f'{var.split(" [")[0].replace(" ", "_")} <- as.factor(data_pe[["{var_name_edit}"]]);\n'
            
        for var, prefix in [(domain_var, parent.model_name), (weight, parent.model_name), (strata, parent.model_name), (index_var, parent.model_name)]:
            if var and var != 'NULL':
                var_edit = format_edit_var(var, prefix + parent.separator)
                r_script += f'{var} <- data_pe[["{var_edit}"]];\n'
                
        all_vars = parent.auxilary_vars + parent.as_factor_var + parent.of_interest_var + parent.domain_var + parent.index_var + parent.strata_var+parent.weight_var
        r_script += f'data_model <- data.frame({", ".join([var.split(" [")[0].replace(" ", "_") for var in all_vars])});\n'
        r_script += f'colnames(data_model) <- sub("^{prefix}\\\\{parent.separator}", "", colnames(data_model))\n'
        
        if parent.of_interest_var:
            var = parent.of_interest_var[0]
            var_name_edit = format_edit_var(var, parent.projection_name + parent.separator)
            if parent.projection_method != "Linear":
                r_script += f'{var.split(" [")[0].replace(" ", "_")} <- as.factor(data_pe[["{var_name_edit}"]]);\n'
            else:
                r_script += f'{var.split(" [")[0].replace(" ", "_")} <- data_pe[["{var_name_edit}"]];\n'
        
        for var in parent.auxilary_vars:
            var_name_edit = format_edit_var(var, parent.projection_name + parent.separator)
            r_script += f'{var.split(" [")[0].replace(" ", "_")} <- data_pe[["{var_name_edit}"]];\n'
        
        for var in parent.as_factor_var:
            var_name_edit = format_edit_var(var, parent.projection_name + parent.separator)
            r_script += f'{var.split(" [")[0].replace(" ", "_")} <- as.factor(data_pe[["{var_name_edit}"]]);\n'

        for var, prefix in [(domain_var, parent.projection_name), (weight, parent.projection_name), (strata, parent.projection_name), (index_var, parent.projection_name)]:
            if var and var != 'NULL':
                var_edit = format_edit_var(var, prefix + parent.separator)
                r_script += f'{var} <- data_pe[["{var_edit}"]];\n'

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
                r_script += f'{var.split(" [")[0].replace(" ", "_")} <- as.factor(data_pe[["{var_name_edit}"]]);\n'
            else:
                r_script += f'{var.split(" [")[0].replace(" ", "_")} <- data_pe[["{var_name_edit}"]];\n'
        
        for var in parent.auxilary_vars:
            var_name_edit = format_edit_var_before(var, parent.separator + parent.model_name)
            r_script += f'{var.split(" [")[0].replace(" ", "_")} <- data_pe[["{var_name_edit}"]];\n'
        
        for var in parent.as_factor_var:
            var_name_edit = format_edit_var_before(var, parent.separator + parent.model_name)
            r_script += f'{var.split(" [")[0].replace(" ", "_")} <- as.factor(data_pe[["{var_name_edit}"]]);\n'

        for var, prefix in [(domain_var, parent.model_name), (weight, parent.model_name), (strata, parent.model_name), (index_var, parent.model_name)]:
            if var and var != 'NULL':
                var_edit = format_edit_var_before(var, parent.separator + prefix)
                r_script += f'{var} <- data_pe[["{var_edit}"]];\n'
                
        all_vars = parent.auxilary_vars + parent.as_factor_var + parent.of_interest_var + parent.domain_var + parent.index_var + parent.strata_var+parent.weight_var
        r_script += f'data_model <- data.frame({", ".join([var.split(" [")[0].replace(" ", "_") for var in all_vars])});\n'
        r_script += f'colnames(data_model) <- sub("\\\\{parent.separator}{prefix}$", "", colnames(data_model))\n'
        
        if parent.of_interest_var:
            var = parent.of_interest_var[0]
            var_name_edit = format_edit_var_before(var, parent.separator + parent.projection_name)
            if parent.projection_method != "Linear":
                r_script += f'{var.split(" [")[0].replace(" ", "_")} <- as.factor(data_pe[["{var_name_edit}"]]);\n'
            else:
                r_script += f'{var.split(" [")[0].replace(" ", "_")} <- data_pe[["{var_name_edit}"]];\n'
        
        for var in parent.auxilary_vars:
            var_name_edit = format_edit_var_before(var, parent.separator + parent.projection_name)
            r_script += f'{var.split(" [")[0].replace(" ", "_")} <- data_pe[["{var_name_edit}"]];\n'
        
        for var in parent.as_factor_var:
            var_name_edit = format_edit_var_before(var, parent.separator + parent.projection_name)
            r_script += f'{var.split(" [")[0].replace(" ", "_")} <- as.factor(data_pe[["{var_name_edit}"]]);\n'
            
        for var, prefix in [(domain_var, parent.projection_name), (weight, parent.projection_name), (strata, parent.projection_name), (index_var, parent.projection_name)]:
            if var and var != 'NULL':
                var_edit = format_edit_var_before(var, parent.separator + prefix)
                r_script += f'{var} <- data_pe[["{var_edit}"]];\n'
        
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
        r_script += f'model_pe <- projection(final_formula, id="{index_var}", weight="{weight}", strata="{strata}", domain={domain_var}, model={model_var}, data_model=data_model, data_proj=data_proj, model_metric={parent.metric}, kfold={parent.k_fold}, grid={parent.grid})\n'
    else:
        if strata == 'NULL':
            r_script += f'model_pe <- projection(formula, id="{index_var}", weight="{weight}", strata={strata}, domain="{domain_var}", model={model_var}, data_model=data_model, data_proj=data_proj, model_metric={parent.metric}, kfold={parent.k_fold}, grid={parent.grid})\n'
        else:
            r_script += f'model_pe <- projection(formula, id="{index_var}", weight="{weight}", strata="{strata}", domain="{domain_var}", model={model_var}, data_model=data_model, data_proj=data_proj, model_metric={parent.metric}, kfold={parent.k_fold}, grid={parent.grid})\n'
        return r_script

def show_r_script(parent):
    """
    Generates an R script based on the given parent object and sets the text of the parent's R script editor.
    Args:
        parent: The parent object that contains the method to generate the R script and the R script editor.
    """
    
    r_script = generate_r_script(parent)
    parent.r_script_edit.setText(r_script)

def get_script(parent):
    """
    Retrieves the text content from the 'r_script_edit' attribute of the given parent object.
    Args:
        parent: An object that contains an attribute 'r_script_edit' which is expected to be a QTextEdit or similar widget.
    Returns:
        str: The text content of the 'r_script_edit' widget as a string.
    """
    
    return parent.r_script_edit.toPlainText()  

def show_options(parent):
    """
    Displays a dialog window with various options for configuring the projection method.
    Parameters:
    parent (QWidget): The parent widget to which this dialog belongs.
    The dialog includes the following options:
    - Model Metric: A combo box to select the model metric.
    - The number of partitions: A line edit to input the number of partitions (k-fold).
    - Grid: A line edit to input the grid size.
    - Epoch (conditionally visible): A line edit to input the number of epochs, visible only if the projection method is "Neural Network".
    - Learning Rate (conditionally visible): A line edit to input the learning rate, visible only if the projection method is "Neural Network".
    The dialog also includes OK and Cancel buttons to confirm or reject the selections.
    The OK button triggers the `set_selection_method` function with the parent and dialog as arguments.
    The Cancel button closes the dialog without saving changes.
    """
    
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
        parent.hidden_unit_label.setVisible(True)
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
    """
    Sets various selection parameters for the parent object based on the current state of the UI elements,
    and then accepts the dialog and shows the R script.
    Parameters:
    parent (object): The parent object that contains the UI elements and attributes to be set.
    dialog (QDialog): The dialog that will be accepted after setting the parameters.
    Attributes Set on Parent:
    - metric (str): The selected model metric from the model_metric_combo UI element.
    - k_fold (str): The k-fold value from the kfold_edit UI element.
    - grid (str): The grid value from the grid_edit UI element.
    - epoch (str): The epoch value from the epoch_edit UI element.
    - learning_rate (str): The learning rate value from the learning_edit UI element.
    Actions:
    - Accepts the dialog.
    - Calls the show_r_script function with the parent object.
    """
    
    # parent.selection_method = parent.method_combo.currentText()
    parent.metric = parent.model_metric_combo.currentText()
    parent.k_fold = parent.kfold_edit.text()
    parent.grid = parent.grid_edit.text()
    parent.epoch = parent.epoch_edit.text()
    parent.learning_rate = parent.learning_edit.text()
    dialog.accept()
    show_r_script(parent)