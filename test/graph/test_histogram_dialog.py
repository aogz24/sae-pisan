import sys
import pytest
import polars as pl
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtCore import Qt
from view.components.graph.HistogramDialog import HistogramDialog
from unittest.mock import MagicMock, Mock

app = QApplication.instance()
if not app:
    app = QApplication(sys.argv)

@pytest.fixture
def histogram_dialog(qtbot):
    parent = QWidget()
    dialog = HistogramDialog(parent)
    qtbot.addWidget(dialog)
    return dialog


def test_ui_initialization(histogram_dialog):
    assert histogram_dialog.windowTitle() == "Histogram"
    # Check that key UI components exist.
    assert histogram_dialog.data_editor_list is not None
    assert histogram_dialog.data_output_list is not None
    assert histogram_dialog.selected_list is not None
    assert histogram_dialog.method_combo is not None
    assert histogram_dialog.graph_option_combo is not None
    assert histogram_dialog.graph_option_spinbox is not None
    assert histogram_dialog.script_box.toPlainText() == ""

def test_set_model(histogram_dialog):
    model1_mock = MagicMock()
    model2_mock = MagicMock()
    model1_mock.get_data.return_value.columns = ['var1', 'var2']
    model1_mock.get_data.return_value.dtypes = [pl.Float64, pl.Utf8]  # Should map to [Numeric] and [String]
    model2_mock.get_data.return_value.columns = ['var3', 'var4']
    model2_mock.get_data.return_value.dtypes = [pl.Float64, pl.Utf8]
    
    histogram_dialog.set_model(model1_mock, model2_mock)
    
    expected_editor = ['var1 [Numeric]', 'var2 [String]']
    expected_output = ['var3 [Numeric]', 'var4 [String]']
    
    assert histogram_dialog.data_editor_model.stringList() == expected_editor
    assert histogram_dialog.data_output_model.stringList() == expected_output

def test_get_column_with_dtype(histogram_dialog):
    mock_model = MagicMock()
    # Create a sample DataFrame using polars (or simulate using a mock object)
    # For simplicity, we'll simulate get_data() as returning an object with columns and dtypes attributes.
    mock_data = Mock()
    mock_data.columns = ["A", "B", "C"]
    mock_data.dtypes = [pl.Float64, pl.Utf8, pl.Float64]
    mock_model.get_data.return_value = mock_data

    result = histogram_dialog.get_column_with_dtype(mock_model)
    expected = ["A [Numeric]", "B [String]", "C [Numeric]"]
    assert result == expected

def test_add_variable(histogram_dialog, qtbot):
    # Set up source lists with some variables.
    histogram_dialog.data_editor_model.setStringList(["Var1 [Numeric]", "Var2 [String]"])
    histogram_dialog.data_output_model.setStringList(["Var3 [Numeric]"])
    # Initially, selected_model is empty.
    histogram_dialog.selected_model.setStringList([])

    # Simulate selection: choose first item from data_editor_list and first from data_output_list.
    histogram_dialog.data_editor_list.setCurrentIndex(histogram_dialog.data_editor_model.index(0, 0))
    histogram_dialog.data_output_list.setCurrentIndex(histogram_dialog.data_output_model.index(0, 0))

    # Call add_variable() which should move only numeric items.
    # "Var2 [String]" should trigger a warning and not be added.
    # (Warning dialogs are shown via QMessageBox; in tests we ignore them.)
    histogram_dialog.add_variable()

    # Check that selected_model contains Var1 and Var3, and they are removed from source lists.
    assert "Var1 [Numeric]" in histogram_dialog.selected_model.stringList()
    assert "Var3 [Numeric]" in histogram_dialog.selected_model.stringList()
    # "Var2 [String]" remains in data_editor_model.
    assert histogram_dialog.data_editor_model.stringList() == ["Var2 [String]"]
    # And data_output_model becomes empty.
    assert histogram_dialog.data_output_model.stringList() == []

def test_remove_variable(histogram_dialog, qtbot):
    # Setup: assume selected_model has one variable and it should be returned to data_editor_model.
    histogram_dialog.selected_model.setStringList(["Var1 [Numeric]"])
    # Set all_columns_model1 to include that variable so that remove_variable() can add it back.
    histogram_dialog.all_columns_model1 = ["Var1 [Numeric]"]
    # Ensure data_editor_model is initially empty.
    histogram_dialog.data_editor_model.setStringList([])

    # Simulate selection in selected_list:
    histogram_dialog.selected_list.setCurrentIndex(histogram_dialog.selected_model.index(0, 0))
    histogram_dialog.remove_variable()

    # After removal, selected_model should be empty, and Var1 should be added back to data_editor_model.
    assert histogram_dialog.selected_model.stringList() == []
    assert "Var1 [Numeric]" in histogram_dialog.data_editor_model.stringList()

def test_get_selected_columns(histogram_dialog):
    # Set the selected_model with some variables.
    histogram_dialog.selected_model.setStringList(["Var1 [Numeric]", "Var2 [String]", "Var3 [Numeric]"])
    # get_selected_columns() should strip type annotations and replace spaces with underscores.
    result = histogram_dialog.get_selected_columns()
    expected = ["Var1", "Var2", "Var3"]
    assert result == expected

@pytest.mark.parametrize(
    "selected_columns, method, graph_option, bin_value, expected_script",
    [
        # Case 1: No columns selected
        (
            [], "Single Histogram", "Bins", 10,
            "Tidak ada kolom yang dipilih."
        ),
        (
            [], "Multiple Histogram", "Bins", 10,
            "Tidak ada kolom yang dipilih."
        ),
        # Case 2: Single Histogram with Bins for one column
        (
            ["Var1"], "Single Histogram", "Bins", 10,
            (
                "# Histogram for Var1\n"
                "histogram_Var1 <- ggplot(data, aes(x = Var1)) +\n"
                "    geom_histogram(bins = 10, fill = sample(colors(), 1)[[1]], color = 'black') +\n"
                "    ggtitle('Histogram: Var1') +\n"
                "    xlab('Var1') +\n"
                "    ylab('Frequency') +\n"
                "    theme_minimal()\n\n"
            ).strip()
        ),
        # Case 3: Single Histogram with Binwidth for one column
        (
            ["Var1"], "Single Histogram", "Binwidth", 5,
            (
                "# Histogram for Var1\n"
                "histogram_Var1 <- ggplot(data, aes(x = Var1)) +\n"
                "    geom_histogram(binwidth = 5, fill = sample(colors(), 1)[[1]], color = 'black') +\n"
                "    ggtitle('Histogram: Var1') +\n"
                "    xlab('Var1') +\n"
                "    ylab('Frequency') +\n"
                "    theme_minimal()\n\n"
            ).strip()
        ),
        # Case 4: Multiple Histogram with Bins for two columns
        (
            ["Var1", "Var2"], "Multiple Histogram", "Bins", 15,
            (
                "# Convert to long format for ggplot compatibility\n"
                "data_long <- pivot_longer(data, cols = c(\"Var1\", \"Var2\"), \n"
                "    names_to = 'variable', values_to = 'value')\n\n"
                "# Create multiple histogram\n"
                "histogram_multiple <- ggplot(data_long, aes(x = value, fill = variable)) +\n"
                "    geom_histogram(bins = 15, alpha = 0.6, position = 'identity') +\n"
                "    ggtitle('Multiple Histogram') +\n"
                "    xlab('Value') +\n"
                "    ylab('Frequency') +\n"
                "    theme_minimal()\n"
            ).strip()
        ),
        # Case 5: Multiple Histogram with Binwidth for two columns
        (
            ["Var1", "Var2"], "Multiple Histogram", "Binwidth", 2,
            (
                "# Convert to long format for ggplot compatibility\n"
                "data_long <- pivot_longer(data, cols = c(\"Var1\", \"Var2\"), \n"
                "    names_to = 'variable', values_to = 'value')\n\n"
                "# Create multiple histogram\n"
                "histogram_multiple <- ggplot(data_long, aes(x = value, fill = variable)) +\n"
                "    geom_histogram(binwidth = 2, alpha = 0.6, position = 'identity') +\n"
                "    ggtitle('Multiple Histogram') +\n"
                "    xlab('Value') +\n"
                "    ylab('Frequency') +\n"
                "    theme_minimal()\n"
            ).strip()
        ),
    ],
)
def test_generate_r_script(histogram_dialog, selected_columns, method, graph_option, bin_value, expected_script):
    # Override get_selected_columns() to return the test columns.
    histogram_dialog.get_selected_columns = lambda: selected_columns
    # Override method_combo.currentText() to return the test method.
    histogram_dialog.method_combo.currentText = lambda: method
    # Override graph_option_combo.currentText() and spinbox value.
    histogram_dialog.graph_option_combo.currentText = lambda: graph_option
    histogram_dialog.graph_option_spinbox.value = lambda: bin_value

    histogram_dialog.generate_r_script()
    script = histogram_dialog.script_box.toPlainText().strip()
    assert expected_script in script
