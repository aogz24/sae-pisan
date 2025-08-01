import sys
import pytest
import polars as pl
from PyQt6.QtWidgets import QApplication, QWidget
from unittest.mock import  MagicMock
from view.components.graph.BoxPlotDialog import BoxPlotDialog

app = QApplication.instance()
if not app:
    app = QApplication(sys.argv)

@pytest.fixture
def boxplot_dialog(qtbot):
    """Membuat instance BoxPlotDialog untuk pengujian"""
    parent = QWidget()
    dialog = BoxPlotDialog(parent)
    qtbot.addWidget(dialog)
    return dialog

def test_ui_initialization(boxplot_dialog):
    """Test apakah elemen UI terinisialisasi dengan benar"""
    assert boxplot_dialog.windowTitle() == "Box Plot"
    assert boxplot_dialog.data_editor_list is not None
    assert boxplot_dialog.data_output_list is not None
    assert boxplot_dialog.selected_list is not None
    assert boxplot_dialog.method_combo is not None
    assert boxplot_dialog.script_box.toPlainText() == ""

def test_set_model(boxplot_dialog):
    model1_mock = MagicMock()
    model1_mock.get_data.return_value.columns = ['var1', 'var2']
    model1_mock.get_data.return_value.dtypes = [pl.Float64, pl.Utf8]
    
    model2_mock = MagicMock()
    model2_mock.get_data.return_value.columns = ['var3', 'var4']
    model2_mock.get_data.return_value.dtypes = [pl.Float64, pl.Utf8]
    
    boxplot_dialog.set_model(model1_mock, model2_mock)
    
    expected_list_1 = ['var1 [Numeric]', 'var2 [String]']
    expected_list_2 = ['var3 [Numeric]', 'var4 [String]']

    assert boxplot_dialog.data_editor_model.stringList() == expected_list_1
    assert boxplot_dialog.data_output_model.stringList() == expected_list_2


def test_get_column_with_dtype(boxplot_dialog):
    """Test apakah get_column_with_dtype menghasilkan nama kolom yang benar"""
    mock_model = MagicMock()
    mock_model.get_data.return_value.columns = ["col1", "col2"]
    mock_model.get_data.return_value.dtypes = [pl.Float64, pl.Utf8]
    
    result = boxplot_dialog.get_column_with_dtype(mock_model)
    assert result == ["col1 [Numeric]", "col2 [String]"]

def test_add_variable(boxplot_dialog, qtbot):
    """Test apakah add_variable bekerja dengan benar"""
    boxplot_dialog.data_editor_model.setStringList(["var1 [Numeric]", "var2 [String]"])
    
    boxplot_dialog.data_editor_list.setCurrentIndex(boxplot_dialog.data_editor_model.index(0, 0))
    boxplot_dialog.add_variable()
    
    assert boxplot_dialog.selected_model.stringList() == ["var1 [Numeric]"]
    assert boxplot_dialog.data_editor_model.stringList() == ["var2 [String]"]

def test_remove_variable(boxplot_dialog, qtbot):
    """Test that remove_variable correctly moves a variable back to data_editor_model."""
    boxplot_dialog.selected_model.setStringList(["var1 [Numeric]"])
    boxplot_dialog.all_columns_model1 = ["var1 [Numeric]"]
    boxplot_dialog.selected_list.setCurrentIndex(boxplot_dialog.selected_model.index(0, 0))
    boxplot_dialog.remove_variable()
    assert boxplot_dialog.selected_model.stringList() == []
    assert boxplot_dialog.data_editor_model.stringList() == ["var1 [Numeric]"]

def test_get_selected_columns(boxplot_dialog):
    """Test apakah get_selected_columns menghasilkan nama kolom yang benar"""
    boxplot_dialog.selected_model.setStringList(["var1 [Numeric]", "var2 [String]"])
    result = boxplot_dialog.get_selected_columns()
    assert result == ['`var1`', '`var2`']

import pytest

@pytest.mark.parametrize("selected_columns, method, expected_script", [
    # Case 1: No columns selected
    ([], "Single Box plot", ""),
    ([], "Multiple Box Plot", ""),
    
    # Case 2: Single Box Plot with one column
    (
        ["`Var1`"],
        "Single Box plot",
        (
            "# Box plot for `Var1`\n"
            "boxplot_Var1 <- ggplot(data, aes(y = `Var1`)) +\n"
            "    geom_boxplot(fill = 'darkorange3') +\n"
            "    ggtitle('Box Plot: Var1') +\n"
            "    ylab('Var1') +\n"
            "    theme_minimal()\n"
        ).strip()
    ),
    
    # Case 3: Single Box Plot with two columns
    (
        ["`Var1`", "`Var2`"],
        "Single Box plot",
        (
            "# Box plot for `Var1`\n"
            "boxplot_Var1 <- ggplot(data, aes(y = `Var1`)) +\n"
            "    geom_boxplot(fill = 'darkorange3') +\n"
            "    ggtitle('Box Plot: Var1') +\n"
            "    ylab('Var1') +\n"
            "    theme_minimal()\n\n"
            "# Box plot for `Var2`\n"
            "boxplot_Var2 <- ggplot(data, aes(y = `Var2`)) +\n"
            "    geom_boxplot(fill = 'darkorange3') +\n"
            "    ggtitle('Box Plot: Var2') +\n"
            "    ylab('Var2') +\n"
            "    theme_minimal()\n"
        ).strip()
    ),

    # Case 4: Multiple Box Plot with two columns
    (
        ["`Var1`", "`Var2`"],
        "Multiple Box Plot",
        (
            "# Convert to long format for ggplot compatibility\n"
            "data_long <- pivot_longer(data, cols = c(`Var1`, `Var2`), \n"
            "    names_to = 'variable', values_to = 'value')\n\n"
            "# Create multiple box plot\n"
            "boxplot_multiple <- ggplot(data_long, aes(x = variable, y = value, fill = variable)) +\n"
            "    geom_boxplot() +\n"
            "    ggtitle('Multiple Box Plot') +\n"
            "    xlab('Variable') +\n"
            "    ylab('Value') +\n"
            "    theme_minimal()\n"
        ).strip()
    ),
])
def test_generate_r_script(boxplot_dialog, selected_columns, method, expected_script):
    boxplot_dialog.get_selected_columns = lambda: selected_columns
    boxplot_dialog.method_combo.currentText = lambda: method
    boxplot_dialog.generate_r_script()
    script = boxplot_dialog.script_box.toPlainText().strip()
    assert script == expected_script
