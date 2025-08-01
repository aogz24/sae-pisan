import sys
import pytest
from PyQt6.QtWidgets import QApplication, QWidget
from view.components.exploration.VariableSelectionDialog import VariableSelectionDialog  
from PyQt6.QtCore import Qt
from unittest.mock import MagicMock
import polars as pl

app = QApplication.instance()
if not app:
    app = QApplication(sys.argv)

@pytest.fixture
def variable_selection_dialog(qtbot):
    parent = QWidget()  
    dialog = VariableSelectionDialog(parent)
    return dialog

def test_ui_initialization(variable_selection_dialog):
    assert variable_selection_dialog.windowTitle() == "Variable Selection"
    assert variable_selection_dialog.data_editor_list is not None
    assert variable_selection_dialog.data_output_list is not None
    assert variable_selection_dialog.dependent_variable_list is not None
    assert variable_selection_dialog.independent_variable_list is not None

def test_set_model(variable_selection_dialog):
    model1_mock = MagicMock()
    model2_mock = MagicMock()
    model1_mock.get_data.return_value.columns = ['var1', 'var2']
    model1_mock.get_data.return_value.dtypes = [pl.Int64, pl.Utf8]  
    model2_mock.get_data.return_value.columns = ['var3']
    model2_mock.get_data.return_value.dtypes = [pl.Int64]
    
    variable_selection_dialog.set_model(model1_mock, model2_mock)
    expected_list1 = ['var1 [Numeric]', 'var2 [String]']
    expected_list2 = ['var3 [Numeric]']
    
    assert variable_selection_dialog.data_editor_model.stringList() == expected_list1
    assert variable_selection_dialog.data_output_model.stringList() == expected_list2

def test_get_column_with_dtype(variable_selection_dialog):
    mock_model = MagicMock()
    mock_model.get_data.return_value = pl.DataFrame({
        "A": [1.0, 2.0, 3.0],
        "B": ['a', 'b', 'c'],
        "C": [7.0, 8.0, 9.0],
    })
    expected_output = ["A [Numeric]", "B [String]", "C [Numeric]"]
    assert variable_selection_dialog.get_column_with_dtype(mock_model) == expected_output

def test_add_dependent_variable(variable_selection_dialog):
    dialog = variable_selection_dialog
    dialog.data_editor_model.setStringList(["Var1 [Numeric]", "Var2 [Numeric]"])
    dialog.data_editor_list.setCurrentIndex(dialog.data_editor_model.index(0, 0))

    dialog.add_dependent_variable()

    assert "Var1 [Numeric]" in dialog.dependent_variable_model.stringList()
    assert "Var1 [Numeric]" not in dialog.data_editor_model.stringList()

def test_add_independent_variable(variable_selection_dialog):
    dialog = variable_selection_dialog
    dialog.data_editor_model.setStringList(["Var1 [Numeric]", "Var2 [Numeric]"])
    dialog.data_editor_list.setCurrentIndex(dialog.data_editor_model.index(1, 0))
    
    dialog.add_independent_variables()
    
    assert "Var2 [Numeric]" in dialog.independent_variable_model.stringList()
    assert "Var2 [Numeric]" not in dialog.data_editor_model.stringList()

def test_remove_variable(variable_selection_dialog):
    dialog = variable_selection_dialog
    dialog.dependent_variable_model.setStringList(["Var1 [Numeric]"])
    dialog.dependent_variable_list.setCurrentIndex(dialog.dependent_variable_model.index(0, 0))
    
    dialog.remove_variable()
    
    assert dialog.dependent_variable_model.stringList() == []

def test_get_selected_dependent_variable(variable_selection_dialog):
    dialog = variable_selection_dialog
    dialog.dependent_variable_model.setStringList(["Var1 [Numeric]"])
    assert dialog.get_selected_dependent_variable() == ["Var1"]

def test_get_selected_independent_variables(variable_selection_dialog):
    dialog = variable_selection_dialog
    dialog.independent_variable_model.setStringList(["Var2 [Numeric]", "Var3 [Numeric]"])
    assert dialog.get_selected_independent_variables() == ["Var2", "Var3"]

import pytest
from unittest.mock import MagicMock

import pytest
from unittest.mock import MagicMock

@pytest.mark.parametrize(
    "dependent_var, independent_vars, methods, expected_script",
    [
        # Case 1: Normal case with forward and backward selection
        (
            ["Var1"],
            ["Var2", "Var3"],
            ["forward", "backward"],
            (
                "# Initial regression model\n"
                "null_model <- lm(`Var1` ~ 1, data=data)\n"
                "full_model <- lm(`Var1` ~ `Var2` + `Var3`, data=data)\n\n"
                "forward_model <- stats::step(null_model, \n"
                "                      scope = list(lower = null_model, upper = full_model), \n"
                "                      direction = \"forward\")\n\n"
                "forward_result <- summary(forward_model)\n\n"
                "backward_model <- stats::step(null_model, \n"
                "                      scope = list(lower = null_model, upper = full_model), \n"
                "                      direction = \"backward\")\n\n"
                "backward_result <- summary(backward_model)\n\n"
            ),
        ),
        # Case 2: No independent variables selected
        (
            ["Var1"],
            [],
            ["forward"],
            ""
        ),
        # Case 3: No dependent variable selected
        (
            [],
            ["Var2", "Var3"],
            ["forward"],
            ""
        ),
        # Case 4: No methods selected
        (
            ["Var1"],
            ["Var2", "Var3"],
            [],
            ""
        ),
        # Case 5: Special characters in variable names
        (
            ["Var-1"],
            ["Var A", "Var&B"],
            ["stepwise"],
            (
                "# Initial regression model\n"
                "null_model <- lm(`Var-1` ~ 1, data=data)\n"
                "full_model <- lm(`Var-1` ~ `Var A` + `Var&B`, data=data)\n\n"
                "stepwise_model <- stats::step(null_model, \n"
                "                      scope = list(lower = null_model, upper = full_model), \n"
                "                      direction = \"stepwise\")\n\n"
                "stepwise_result <- summary(stepwise_model)\n\n"
            ),
        ),
    ],
)
def test_generate_r_script(variable_selection_dialog, dependent_var, independent_vars, methods, expected_script):
    dialog = variable_selection_dialog

    # Mock data
    dialog.get_selected_dependent_variable = MagicMock(return_value=dependent_var)
    dialog.get_selected_independent_variables = MagicMock(return_value=independent_vars)
    dialog.get_selected_methods = MagicMock(return_value=methods)

    # Mock script output
    dialog.script_box = MagicMock()

    # Run the function
    dialog.generate_r_script()

    # Check the script content
    dialog.script_box.setPlainText.assert_called_once_with(expected_script)
