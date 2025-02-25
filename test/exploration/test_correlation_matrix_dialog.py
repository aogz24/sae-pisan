import sys
import pytest
import polars as pl
from PyQt6.QtWidgets import QApplication, QWidget
from view.components.exploration.CorrelationMatrikDialog import CorrelationMatrixDialog
from unittest.mock import Mock

app = QApplication.instance()
if not app:
    app = QApplication(sys.argv)

@pytest.fixture
def correlation_matrix_dialog(qtbot):
    """Membuat instance CorrelationMatrixDialog untuk pengujian"""
    parent = QWidget()
    dialog = CorrelationMatrixDialog(parent)
    qtbot.addWidget(dialog)
    return dialog

def test_ui_initialization(correlation_matrix_dialog):
    """Test apakah elemen UI terinisialisasi dengan benar"""
    assert correlation_matrix_dialog.windowTitle() == "Correlation"
    assert correlation_matrix_dialog.data_editor_list is not None
    assert correlation_matrix_dialog.correlation_plot_checkbox is not None
    assert correlation_matrix_dialog.script_box.toPlainText() == ""

def test_get_column_with_dtype(correlation_matrix_dialog):
    """Test if get_column_with_dtype returns the correct formatted column names."""
    mock_model = Mock()
    mock_model.get_data.return_value.columns = ["col1", "col2"]
    mock_model.get_data.return_value.dtypes = [pl.Float64, pl.Utf8]

    result = correlation_matrix_dialog.get_column_with_dtype(mock_model)
    assert result == ["col1 [Numeric]", "col2 [String]"]


def test_add_variable(correlation_matrix_dialog, qtbot):
    """Test if add_variable correctly moves numeric variables to the selected list."""
    correlation_matrix_dialog.data_editor_model.setStringList(["var1 [Numeric]", "var2 [String]"])
    correlation_matrix_dialog.data_output_model.setStringList(["var3 [Numeric]"])

    correlation_matrix_dialog.data_editor_list.setCurrentIndex(correlation_matrix_dialog.data_editor_model.index(0, 0))
    correlation_matrix_dialog.data_output_list.setCurrentIndex(correlation_matrix_dialog.data_output_model.index(0, 0))

    correlation_matrix_dialog.add_variable()

    assert correlation_matrix_dialog.selected_model.stringList() == ["var1 [Numeric]", "var3 [Numeric]"]
    assert correlation_matrix_dialog.data_editor_model.stringList() == ["var2 [String]"]
    assert correlation_matrix_dialog.data_output_model.stringList() == []


def test_remove_variable(correlation_matrix_dialog, qtbot):
    """Test if remove_variable correctly moves variables back to their respective lists."""
    correlation_matrix_dialog.selected_model.setStringList(["var1 [Numeric]", "var3 [Numeric]"])
    correlation_matrix_dialog.all_columns_model1 = ["var1 [Numeric]"]
    correlation_matrix_dialog.all_columns_model2 = ["var3 [Numeric]"]

    correlation_matrix_dialog.selected_list.setCurrentIndex(correlation_matrix_dialog.selected_model.index(0, 0))
    
    correlation_matrix_dialog.remove_variable()

    assert correlation_matrix_dialog.selected_model.stringList() == ["var3 [Numeric]"]
    assert correlation_matrix_dialog.data_editor_model.stringList() == ["var1 [Numeric]"]
    assert correlation_matrix_dialog.data_output_model.stringList() == []


def test_get_selected_columns(correlation_matrix_dialog):
    """Test if get_selected_columns returns only the column names without data type annotations."""
    correlation_matrix_dialog.selected_model.setStringList(["var1 [Numeric]", "var2 [String]", "var3 [Numeric]"])

    result = correlation_matrix_dialog.get_selected_columns()
    
    assert result == ["var1", "var2", "var3"]


def test_generate_r_script_no_selection(correlation_matrix_dialog):
    """Test jika tidak ada kolom yang dipilih, script harus kosong."""
    correlation_matrix_dialog.generate_r_script()
    assert correlation_matrix_dialog.script_box.toPlainText() == ""

def test_generate_r_script_with_columns(correlation_matrix_dialog):
    """Test jika beberapa kolom numerik dipilih, apakah script R dihasilkan dengan benar."""
    correlation_matrix_dialog.selected_model.setStringList(["var1 [Numeric]", "var2 [Numeric]"])
    correlation_matrix_dialog.generate_r_script()
    expected_script = """
correlation_matrix <- cor(data[, c("var1", "var2")], use="complete.obs", method="pearson")
    """.strip()
    assert expected_script in correlation_matrix_dialog.script_box.toPlainText()

def test_generate_r_script_with_plot(correlation_matrix_dialog):
    """Test jika checkbox plot diaktifkan, apakah script R juga mencantumkan ggcorrplot."""
    correlation_matrix_dialog.selected_model.setStringList(["var1 [Numeric]", "var2 [Numeric]"])
    correlation_matrix_dialog.correlation_plot_checkbox.setChecked(True)
    correlation_matrix_dialog.generate_r_script()
    assert "ggcorrplot(correlation_matrix" in correlation_matrix_dialog.script_box.toPlainText()

