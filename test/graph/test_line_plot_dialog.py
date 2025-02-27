import sys
import pytest
import polars as pl
from PyQt6.QtWidgets import QApplication, QWidget, QMessageBox
from PyQt6.QtCore import Qt, QStringListModel
from unittest.mock import MagicMock, Mock
from view.components.graph.LinePlotDialog import LinePlotDialog


app = QApplication.instance()
if not app:
    app = QApplication(sys.argv)

@pytest.fixture
def line_plot_dialog(qtbot):
    parent = QWidget()
    dialog = LinePlotDialog(parent)
    qtbot.addWidget(dialog)
    return dialog

def test_ui_initialization(line_plot_dialog):
    assert line_plot_dialog.windowTitle() == "Line Plot"
    assert line_plot_dialog.data_editor_list is not None
    assert line_plot_dialog.data_output_list is not None
    assert line_plot_dialog.horizontal_list is not None
    assert line_plot_dialog.vertical_list is not None
    assert line_plot_dialog.method_combo is not None
    assert line_plot_dialog.script_box.toPlainText() == ""

def test_set_model(line_plot_dialog):
    model1_mock = MagicMock()
    model2_mock = MagicMock()
    model1_mock.get_data.return_value.columns = ['A', 'B']
    model1_mock.get_data.return_value.dtypes = [pl.Float64, pl.Utf8]
    model2_mock.get_data.return_value.columns = ['C']
    model2_mock.get_data.return_value.dtypes = [pl.Int64]
    line_plot_dialog.set_model(model1_mock, model2_mock)
    expected_editor = ['A [Numeric]', 'B [String]']
    expected_output = ['C [Numeric]']
    assert line_plot_dialog.data_editor_model.stringList() == expected_editor
    assert line_plot_dialog.data_output_model.stringList() == expected_output

def test_get_column_with_dtype(line_plot_dialog):
    mock_model = MagicMock()
    mock_data = Mock()
    mock_data.columns = ["X", "Y", "Z"]
    mock_data.dtypes = [pl.Float64, pl.Utf8, pl.Int64]
    mock_model.get_data.return_value = mock_data
    result = line_plot_dialog.get_column_with_dtype(mock_model)
    expected = ["X [Numeric]", "Y [String]", "Z [Numeric]"]
    assert result == expected

def test_add_variable_horizontal(line_plot_dialog, qtbot):
    if not hasattr(line_plot_dialog, "horizontal_model"):
        line_plot_dialog.horizontal_model = QStringListModel()
        line_plot_dialog.horizontal_list.setModel(line_plot_dialog.horizontal_model)
    line_plot_dialog.data_editor_model.setStringList(["Time [Numeric]", "Other [Numeric]"])
    line_plot_dialog.data_editor_list.setCurrentIndex(line_plot_dialog.data_editor_model.index(0, 0))
    line_plot_dialog.add_variable_horizontal()
    assert "Time [Numeric]" in line_plot_dialog.horizontal_model.stringList()
    assert "Time [Numeric]" not in line_plot_dialog.data_editor_model.stringList()

def test_add_variable_vertical(line_plot_dialog, qtbot):
    line_plot_dialog.data_editor_model.setStringList(["VarA [Numeric]", "VarB [String]"])
    line_plot_dialog.data_output_model.setStringList(["VarC [Numeric]"])
    if not hasattr(line_plot_dialog, "vertical_model") or line_plot_dialog.vertical_model is None:
        line_plot_dialog.vertical_model = QStringListModel()
        line_plot_dialog.vertical_list.setModel(line_plot_dialog.vertical_model)
    line_plot_dialog.data_editor_list.setCurrentIndex(line_plot_dialog.data_editor_model.index(0, 0))
    line_plot_dialog.data_output_list.setCurrentIndex(line_plot_dialog.data_output_model.index(0, 0))
    line_plot_dialog.add_variable_vertical()
    vertical = line_plot_dialog.vertical_model.stringList()
    assert "VarA [Numeric]" in vertical
    assert "VarC [Numeric]" in vertical
    assert "VarB [String]" in line_plot_dialog.data_editor_model.stringList()

def test_remove_variable(line_plot_dialog, qtbot):
    if not hasattr(line_plot_dialog, "horizontal_model"):
        line_plot_dialog.horizontal_model = QStringListModel()
        line_plot_dialog.horizontal_list.setModel(line_plot_dialog.horizontal_model)
    line_plot_dialog.horizontal_model.setStringList(["Time [Numeric]"])
    line_plot_dialog.all_columns_model1 = ["Time [Numeric]"]
    line_plot_dialog.data_editor_model.setStringList([])
    line_plot_dialog.horizontal_list.setCurrentIndex(line_plot_dialog.horizontal_model.index(0, 0))
    line_plot_dialog.remove_variable()
    assert line_plot_dialog.horizontal_model.stringList() == []
    assert "Time [Numeric]" in line_plot_dialog.data_editor_model.stringList()

def test_get_selected_horizontal(line_plot_dialog):
    if not hasattr(line_plot_dialog, "horizontal_model") or line_plot_dialog.horizontal_model is None:
        line_plot_dialog.horizontal_model = QStringListModel()
        line_plot_dialog.horizontal_list.setModel(line_plot_dialog.horizontal_model)
    line_plot_dialog.horizontal_model.setStringList(["Time [Numeric]"])
    result = line_plot_dialog.get_selected_horizontal()
    assert result == ["Time"]

def test_get_selected_vertical(line_plot_dialog):
    if not hasattr(line_plot_dialog, "vertical_model") or line_plot_dialog.vertical_model is None:
        line_plot_dialog.vertical_model = QStringListModel()
        line_plot_dialog.vertical_list.setModel(line_plot_dialog.vertical_model)
    line_plot_dialog.vertical_model.setStringList(["Value [Numeric]", "Pressure [Numeric]"])
    result = line_plot_dialog.get_selected_vertical()
    assert result == ["Value", "Pressure"]

@pytest.mark.parametrize(
    "horizontal, vertical, method, expected_script",
    [
        # Case 1: Single Lineplot with two vertical variables.
        (
            ["Time"], ["Value", "Pressure"], "Single Lineplot",
            (
                "# Line plot for Time vs. Value\n"
                "lineplot_Value <- ggplot(data, aes(x = Time, y = Value)) +\n"
                "    geom_line(color = sample(colors(), 1)) +\n"
                "    ggtitle(\"Line Plot: Time vs. Value\") +\n"
                "    xlab(\"Time\") +\n"
                "    ylab(\"Value\") +\n"
                "    theme_minimal()\n\n"
                "# Line plot for Time vs. Pressure\n"
                "lineplot_Pressure <- ggplot(data, aes(x = Time, y = Pressure)) +\n"
                "    geom_line(color = sample(colors(), 1)) +\n"
                "    ggtitle(\"Line Plot: Time vs. Pressure\") +\n"
                "    xlab(\"Time\") +\n"
                "    ylab(\"Pressure\") +\n"
                "    theme_minimal()\n"
            ).strip()
        ),
        # Case 2: Multiple Lineplot with two vertical variables.
        (
            ["Time"], ["Value", "Pressure"], "Multiple Lineplot",
            (
                "# Multiple line plot for Time vs. multiple y variables\n\n"
                "# Convert to long format for ggplot\n"
                "data_long <- pivot_longer(data, cols = c(\"Value\", \"Pressure\"),\n"
                "                        names_to = \"variable\", values_to = \"value\")\n\n"
                "# Create line plot\n"
                "lineplot_multiple <- ggplot(data_long, aes(x = Time, y = value, color = variable)) +\n"
                "    geom_line() +\n"
                "    ggtitle(\"Multiple Line Plot: Time vs. Value, Pressure\") +\n"
                "    xlab(\"Time\") +\n"
                "    ylab(\"Value\") +\n"
                "    theme_minimal()\n"
            ).strip()
        ),
    ]
)
def test_generate_r_script(line_plot_dialog, qtbot, horizontal, vertical, method, expected_script):
    # Override selection methods to simulate user input.
    line_plot_dialog.get_selected_horizontal = lambda: horizontal
    line_plot_dialog.get_selected_vertical = lambda: vertical
    # Override method_combo.currentText() to return our test method.
    line_plot_dialog.method_combo.currentText = lambda: method
    
    # Generate the R script.
    line_plot_dialog.generate_r_script()
    script = line_plot_dialog.script_box.toPlainText().strip()
    
    # Assert that the expected script is contained in the generated script.
    assert expected_script in script
