import sys
import pytest
from PyQt6.QtWidgets import QApplication, QWidget
from view.components.exploration.MulticollinearityDialog import MulticollinearityDialog
from PyQt6.QtCore import Qt
from unittest.mock import MagicMock
import polars as pl

# Pastikan aplikasi Qt berjalan saat dijalankan langsung
app = QApplication.instance()
if not app:
    app = QApplication(sys.argv)

@pytest.fixture
def multicollinearity_dialog(qtbot):
    """Membuat instance MulticollinearityDialog untuk pengujian"""
    parent = QWidget()
    dialog = MulticollinearityDialog(parent)
    qtbot.addWidget(dialog)  
    return dialog

def test_ui_initialization(multicollinearity_dialog):
    """Test apakah elemen UI terinisialisasi dengan benar"""
    assert multicollinearity_dialog.windowTitle() == "Multicollinearity"
    assert multicollinearity_dialog.data_editor_list is not None
    assert multicollinearity_dialog.data_output_list is not None
    assert multicollinearity_dialog.independent_variable_list is not None
    assert multicollinearity_dialog.dependent_variable_list is not None
    assert multicollinearity_dialog.script_box.toPlainText() == ""

def test_get_column_with_dtype(multicollinearity_dialog):
    """Test apakah get_column_with_dtype mengembalikan format yang benar"""
    mock_model = MagicMock()
    mock_model.get_data.return_value = pl.DataFrame({
        "A": [1.0, 2.0, 3.0],
        "B": [4.0, 5.0, 6.0],
        "C": [7.0, 8.0, 9.0],
    })
    expected_output = ["A [Numeric]", "B [Numeric]", "C [Numeric]"]
    assert multicollinearity_dialog.get_column_with_dtype(mock_model) == expected_output

def test_add_variable_dependent_variable(multicollinearity_dialog, qtbot):
    multicollinearity_dialog.data_editor_model.setStringList(["A [Numeric]", "B [Numeric]"])
    multicollinearity_dialog.data_editor_list.setCurrentIndex(multicollinearity_dialog.data_editor_model.index(0))
    multicollinearity_dialog.add_variable_dependent_variable()
    assert multicollinearity_dialog.dependent_variable_model.stringList() == ["A [Numeric]"]

def test_add_variable_independent_variables(multicollinearity_dialog, qtbot):
    multicollinearity_dialog.data_editor_model.setStringList(["A [Numeric]", "B [Numeric]"])
    multicollinearity_dialog.data_editor_list.setCurrentIndex(multicollinearity_dialog.data_editor_model.index(1))
    multicollinearity_dialog.add_variable_independent_variables()
    assert multicollinearity_dialog.independent_variable_model.stringList() == ["B [Numeric]"]

def test_remove_variable(multicollinearity_dialog, qtbot):
    multicollinearity_dialog.dependent_variable_model.setStringList(["A [Numeric]"])
    multicollinearity_dialog.independent_variable_model.setStringList(["B [Numeric]"])
    multicollinearity_dialog.dependent_variable_list.setCurrentIndex(multicollinearity_dialog.dependent_variable_model.index(0))
    multicollinearity_dialog.remove_variable()
    assert multicollinearity_dialog.dependent_variable_model.stringList() == []
    assert multicollinearity_dialog.independent_variable_model.stringList() == ["B [Numeric]"]

def test_get_selected_dependent_variable(multicollinearity_dialog):
    multicollinearity_dialog.dependent_variable_model.setStringList(["A [Numeric]"])
    assert multicollinearity_dialog.get_selected_dependent_variable() == ["A"]

def test_get_selected_independent_variables(multicollinearity_dialog):
    multicollinearity_dialog.independent_variable_model.setStringList(["B [Numeric]", "C [Numeric]"])
    assert multicollinearity_dialog.get_selected_independent_variables() == ["B", "C"]

def test_generate_r_script(multicollinearity_dialog):
    multicollinearity_dialog.get_selected_dependent_variable = MagicMock(return_value=["A"])
    multicollinearity_dialog.get_selected_independent_variables = MagicMock(return_value=["B","C"])
    multicollinearity_dialog.generate_r_script()
    expected_script = "regression_model <- lm(`A` ~ `B` + `C`, data=data)\nvif_values <- vif(regression_model)\n"
    assert multicollinearity_dialog.script_box.toPlainText() == expected_script