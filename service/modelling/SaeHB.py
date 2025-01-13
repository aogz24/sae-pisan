def assign_dependent(parent):
    selected_indexes = parent.variables_list.selectedIndexes()
    parent.dependent_var = [index.data() for index in selected_indexes]
    parent.dependent_model.setStringList(parent.dependent_var)

def assign_independent(parent):
    selected_indexes = parent.variables_list.selectedIndexes()
    if selected_indexes:
        parent.independent_vars = [selected_indexes[-1].data()]
        parent.independent_model.setStringList(parent.independent_vars)

def assign_vardir(parent):
    selected_indexes = parent.variables_list.selectedIndexes()
    if selected_indexes:
        parent.vardir_var = [selected_indexes[-1].data()]
        parent.vardir_model.setStringList(parent.vardir_var)

def unassign_variable(parent):
    selected_indexes = parent.dependent_list.selectedIndexes()
    if selected_indexes:
        selected_items = [index.data() for index in selected_indexes]
        parent.dependent_var = [var for var in parent.dependent_var if var not in selected_items]
        parent.dependent_model.setStringList(parent.dependent_var)
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