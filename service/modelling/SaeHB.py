def assign_dependent(parent):
    selected_indexes = parent.variables_list.selectedIndexes()
    if selected_indexes:
        parent.dependent_var = [selected_indexes[-1].data()]  # Only allow one dependent variable
        parent.dependent_model.setStringList(parent.dependent_var)
        parent.variables_list.model().removeRow(selected_indexes[-1].row())  # Remove from variables list

def assign_independent(parent):
    selected_indexes = parent.variables_list.selectedIndexes()
    if selected_indexes:
        new_vars = [index.data() for index in selected_indexes]
        parent.independent_vars = list(set(parent.independent_vars + new_vars))  # Add new variables if they are different
        parent.independent_model.setStringList(parent.independent_vars)
        for index in selected_indexes:
            parent.variables_list.model().removeRow(index.row())  # Remove from variables list

def assign_vardir(parent):
    selected_indexes = parent.variables_list.selectedIndexes()
    if selected_indexes:
        parent.vardir_var = [selected_indexes[-1].data()]
        parent.vardir_model.setStringList(parent.vardir_var)
        parent.variables_list.model().removeRow(selected_indexes[-1].row())  # Remove from variables list

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

def get_selected_variables(parent):
    return parent.dependent_var, parent.independent_vars, parent.vardir_var

def generate_r_script(parent):
    dependent_var = f'"{parent.dependent_var[0].split(" [")[0]}"' if parent.dependent_var else '""'
    independent_vars = " + ".join([f'"{var.split(" [")[0]}"' for var in parent.independent_vars])
    vardir_var = f'"{parent.vardir_var[0].split(" [")[0]}"' if parent.vardir_var else '""'

    r_script = f'mseFH({dependent_var} ~ {independent_vars}, {vardir_var}, method = "REML", MAXITER = 100, PRECISION = 0.0001, B = 0, data)'
    return r_script

def show_r_script(parent):
    r_script = generate_r_script(parent)
    parent.r_script_edit.setText(r_script)