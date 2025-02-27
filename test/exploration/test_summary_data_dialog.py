import sys
import pytest
from PyQt6.QtWidgets import QApplication, QWidget
from view.components.exploration.SummaryDataDialog import SummaryDataDialog
from PyQt6.QtCore import Qt
from unittest.mock import MagicMock
import polars as pl

app = QApplication.instance()
if not app:
    app = QApplication(sys.argv)

@pytest.fixture
def summary_dialog(qtbot):
    """Membuat instance SummaryDataDialog untuk pengujian"""
    parent = QWidget()  
    dialog = SummaryDataDialog(parent)
    return dialog

def test_ui_initialization(summary_dialog):
    """Test apakah elemen UI terinisialisasi dengan benar"""
    assert summary_dialog.windowTitle() == "Summary Data"
    assert summary_dialog.data_editor_list is not None
    assert summary_dialog.data_output_list is not None
    assert summary_dialog.selected_list is not None
    assert summary_dialog.script_box.toPlainText() == ""

def test_set_model(summary_dialog):
    model1_mock = MagicMock()
    model2_mock = MagicMock()
    model1_mock.get_data.return_value.columns = ['var1', 'var2']
    model1_mock.get_data.return_value.dtypes = [pl.Int64, pl.Utf8]  # Perbaikan mapping tipe data
    model2_mock.get_data.return_value.columns = ['var3']
    model2_mock.get_data.return_value.dtypes = [pl.Int64]
    
    summary_dialog.set_model(model1_mock, model2_mock)
    
    expected_list_1 = ['var1 [Numeric]', 'var2 [String]']
    expected_list_2 = ['var3 [Numeric]']
    
    assert summary_dialog.data_editor_model.stringList() == expected_list_1
    assert summary_dialog.data_output_model.stringList() == expected_list_2

def test_get_column_with_dtype(summary_dialog):
    """Test apakah get_column_with_dtype mengembalikan format yang benar"""

    mock_model = MagicMock()
    mock_model.get_data.return_value.columns = ["A", "B", "C"]
    mock_model.get_data.return_value.dtypes = [pl.Utf8, pl.Float64, pl.Int64]

    expected_output = ["A [String]", "B [Numeric]", "C [Numeric]"]

    assert summary_dialog.get_column_with_dtype(mock_model) == expected_output

def test_get_selected_columns(summary_dialog):
    """Test apakah get_selected_columns mengembalikan nama kolom dengan benar"""
    summary_dialog.selected_model.setStringList(["A [String]", "B [Numeric]", "C [Numeric]"])
    expected_output = ["A", "B", "C"]
    assert summary_dialog.get_selected_columns() == expected_output

def test_add_variable(summary_dialog, qtbot):
    """Test apakah variabel dapat ditambahkan ke daftar selected_list"""
    summary_dialog.data_editor_model.setStringList(["A [Numeric]", "B [Numeric]"])
    summary_dialog.data_output_model.setStringList(["X [Numeric]"])
    summary_dialog.data_editor_list.setCurrentIndex(summary_dialog.data_editor_model.index(0))
    summary_dialog.data_output_list.setCurrentIndex(summary_dialog.data_output_model.index(0))

    qtbot.mouseClick(summary_dialog.add_button, Qt.MouseButton.LeftButton)

    assert summary_dialog.selected_model.stringList() == ["A [Numeric]", "X [Numeric]"]

def test_remove_variable(summary_dialog, qtbot):
    """Test apakah variabel dapat dihapus dari daftar selected_list"""
    summary_dialog.selected_model.setStringList(["A [Numeric]", "B [Numeric]"])

    summary_dialog.selected_list.setCurrentIndex(summary_dialog.selected_model.index(0))

    qtbot.mouseClick(summary_dialog.remove_button, Qt.MouseButton.LeftButton)

    assert summary_dialog.selected_model.stringList() == ["B [Numeric]"]

def test_generate_r_script(summary_dialog):
    """Test apakah generate_r_script bekerja dengan benar"""
    summary_dialog.selected_model.setStringList(["A [Numeric]", "B [Numeric]"])
    summary_dialog.generate_r_script()
    expected_script = 'summary_results <- summary(data[, c("A", "B")])'
    assert summary_dialog.script_box.toPlainText() == expected_script

if __name__ == "__main__":
    pytest.main([__file__])
