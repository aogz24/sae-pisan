import sys
import pytest
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtCore import Qt
from view.components.graph.ScatterPlotDialog import ScatterPlotDialog
from unittest.mock import MagicMock, Mock
import polars as pl

app = QApplication.instance()
if not app:
    app = QApplication(sys.argv)

@pytest.fixture
def scatter_plot_dialog(qtbot):
    parent = QWidget()
    dialog = ScatterPlotDialog(parent)
    qtbot.addWidget(dialog)
    return dialog
def test_ui_initialization(scatter_plot_dialog):
    assert scatter_plot_dialog.windowTitle() == "Scatter Plot"
    assert scatter_plot_dialog.data_editor_list is not None
    assert scatter_plot_dialog.data_output_list is not None
    assert scatter_plot_dialog.selected_list is not None
    # Assume script_box is empty initially.
    assert scatter_plot_dialog.script_box.toPlainText() == ""

def test_set_model(scatter_plot_dialog):
    model1_mock = MagicMock()
    model2_mock = MagicMock()
    model1_mock.get_data.return_value.columns = ['A', 'B']
    # For this test, assume pl.Float64 maps to "Numeric" and pl.Utf8 maps to "Utf8"
    model1_mock.get_data.return_value.dtypes = [pl.Float64, pl.Utf8]
    model2_mock.get_data.return_value.columns = ['C']
    model2_mock.get_data.return_value.dtypes = [pl.Int64]
    
    scatter_plot_dialog.set_model(model1_mock, model2_mock)
    
    expected_editor = ['A [Numeric]', 'B [String]']
    expected_output = ['C [Numeric]']
    
    assert scatter_plot_dialog.data_editor_model.stringList() == expected_editor
    assert scatter_plot_dialog.data_output_model.stringList() == expected_output

def test_get_column_with_dtype(scatter_plot_dialog):
    mock_model = MagicMock()
    mock_data = Mock()
    mock_data.columns = ["X", "Y", "Z"]
    mock_data.dtypes = [pl.Float64, pl.Utf8, pl.Int64]
    mock_model.get_data.return_value = mock_data
    result = scatter_plot_dialog.get_column_with_dtype(mock_model)
    expected = ["X [Numeric]", "Y [String]", "Z [Numeric]"]
    assert result == expected

def test_add_variable(scatter_plot_dialog, qtbot):
    # Setup: data_editor_model and data_output_model contain variables.
    scatter_plot_dialog.data_editor_model.setStringList(["A [Numeric]", "B [String]"])
    scatter_plot_dialog.data_output_model.setStringList(["C [Numeric]"])
    # Clear selected_model
    scatter_plot_dialog.selected_model.setStringList([])

    # Simulate selecting the first item from data_editor_list and first item from data_output_list.
    scatter_plot_dialog.data_editor_list.setCurrentIndex(scatter_plot_dialog.data_editor_model.index(0, 0))
    scatter_plot_dialog.data_output_list.setCurrentIndex(scatter_plot_dialog.data_output_model.index(0, 0))

    scatter_plot_dialog.add_variable()

    # Expected: selected_model should now contain ["A [Numeric]", "C [Numeric]"].
    assert scatter_plot_dialog.selected_model.stringList() == ["A [Numeric]", "C [Numeric]"]
    # "A [Numeric]" is removed from data_editor_model, and "C [Numeric]" from data_output_model.
    # Since "B [String]" originally belonged to the data editor list, it remains there.
    assert scatter_plot_dialog.data_editor_model.stringList() == ["B [String]"]
    assert scatter_plot_dialog.data_output_model.stringList() == []

def test_remove_variable(scatter_plot_dialog):
    # Setup: selected_model contains one variable that should be returned to data_editor_model.
    scatter_plot_dialog.selected_model.setStringList(["A [Numeric]"])
    scatter_plot_dialog.all_columns_model1 = ["A [Numeric]"]
    # Ensure data_editor_model is initially empty.
    scatter_plot_dialog.data_editor_model.setStringList([])
    # Simulate that the variable is selected in the selected_list.
    scatter_plot_dialog.selected_list.setCurrentIndex(scatter_plot_dialog.selected_model.index(0, 0))
    
    scatter_plot_dialog.remove_variable()
    
    # After removal, selected_model should be empty and "A [Numeric]" should appear in data_editor_model.
    assert scatter_plot_dialog.selected_model.stringList() == []
    assert "A [Numeric]" in scatter_plot_dialog.data_editor_model.stringList()

def test_get_selected_columns(scatter_plot_dialog):
    # Setup: selected_model contains variables with type annotations and spaces.
    scatter_plot_dialog.selected_model.setStringList(["Var1 [Numeric]",  "Var3 [Numeric]"])
    result = scatter_plot_dialog.get_selected_columns()
    # Expected: remove type annotations and replace spaces with underscores.
    expected = ["Var1", "Var3"]
    assert result == expected

import pytest

@pytest.mark.parametrize(
    "selected_columns, show_regression, show_correlation, show_density, expected_script",
    [
        (
            ["Var1", "Var2"],
            False,
            False,
            False,
            (
                'data_plot <- data[, c("Var1", "Var2")]\n\n'
                'scatterplot <- ggpairs(\n'
                '    data_plot,\n'
                '    lower = list(continuous = "points"),\n'
                '    upper = list(continuous = "blank"),\n'
                '    diag = list(continuous = "blankDiag")\n'
                ')'
            )
        ),
        (
            ["Var1", "Var2"],
            True,
            True,
            True,
            (
                'data_plot <- data[, c("Var1", "Var2")]\n\n'
                'scatterplot <- ggpairs(\n'
                '    data_plot,\n'
                '    lower = list(continuous = wrap("smooth", method="lm")),\n'
                '    upper = list(continuous = "cor"),\n'
                '    diag = list(continuous = "densityDiag")\n'
                ')'
            )
        ),
    ]
)
def test_generate_r_script(scatter_plot_dialog, qtbot, selected_columns, show_regression, show_correlation, show_density, expected_script):
    scatter_plot_dialog.get_selected_columns = lambda: selected_columns
    scatter_plot_dialog.regression_line_checkbox.setChecked(show_regression)
    scatter_plot_dialog.correlation_checkbox.setChecked(show_correlation)
    scatter_plot_dialog.density_plot_checkbox.setChecked(show_density)

    scatter_plot_dialog.generate_r_script()
    script = scatter_plot_dialog.script_box.toPlainText().strip()
    assert script == expected_script
