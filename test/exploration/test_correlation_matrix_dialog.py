import sys
import pytest
import polars as pl
from PyQt6.QtWidgets import QApplication, QWidget
from view.components.exploration.CorrelationMatrikDialog import CorrelationMatrixDialog
from unittest.mock import Mock, MagicMock

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

def test_set_model(correlation_matrix_dialog):
    model1_mock = MagicMock()
    model2_mock = MagicMock()
    model1_mock.get_data.return_value.columns = ['var1', 'var2']
    model1_mock.get_data.return_value.dtypes = [pl.Int64, pl.Utf8]  # Perbaikan mapping tipe data
    model2_mock.get_data.return_value.columns = ['var3']
    model2_mock.get_data.return_value.dtypes = [pl.Int64]
    
    correlation_matrix_dialog.set_model(model1_mock, model2_mock)
    
    expected_list_1 = ['var1 [Numeric]', 'var2 [String]']
    expected_list_2 = ['var3 [Numeric]']
    
    assert correlation_matrix_dialog.data_editor_model.stringList() == expected_list_1
    assert correlation_matrix_dialog.data_output_model.stringList() == expected_list_2
    
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


import pytest

@pytest.mark.parametrize(
    "selected_columns, method_checked, plot_checked, expected_parts",
    [
        # Tidak ada kolom → script kosong
        ([], "pearson", False, []),

        # Hanya pearson, tanpa plot
        (
            ["var1 [Numeric]", "var2 [Numeric]"],
            "pearson",
            False,
            [
                'correlation_matrix_pearson <- cor(data[, c("var1", "var2")], use=\'complete.obs\', method=\'pearson\')'
            ]
        ),

        # Pearson + plot
        (
            ["var1 [Numeric]", "var2 [Numeric]"],
            "pearson",
            True,
            [
                'correlation_matrix_pearson <- cor(data[, c("var1", "var2")], use=\'complete.obs\', method=\'pearson\')',
                'correlation_plot_pearson <- ggcorrplot(correlation_matrix_pearson, method = \'square\', type = \'upper\', lab = TRUE) + ggtitle(\'Pearson Correlation Matrix\')'
            ]
        ),

        # Spearman + plot
        (
            ["var1 [Numeric]", "var2 [Numeric]"],
            "spearman",
            True,
            [
                'correlation_matrix_spearman <- cor(data[, c("var1", "var2")], use=\'complete.obs\', method=\'spearman\')',
                'correlation_plot_spearman <- ggcorrplot(correlation_matrix_spearman, method = \'square\', type = \'upper\', lab = TRUE) + ggtitle(\'Spearman Correlation Matrix\')'
            ]
        ),
    ],
)
def test_generate_r_script(correlation_matrix_dialog, selected_columns, method_checked, plot_checked, expected_parts):
    # Set kolom
    correlation_matrix_dialog.selected_model.setStringList(selected_columns)
    correlation_matrix_dialog.correlation_plot_checkbox.setChecked(plot_checked)

    # Set metode yang dicentang
    correlation_matrix_dialog.pearson_checkbox.setChecked(method_checked == "pearson")
    correlation_matrix_dialog.spearman_checkbox.setChecked(method_checked == "spearman")
    correlation_matrix_dialog.kendall_checkbox.setChecked(method_checked == "kendall")

    # Jalankan fungsi
    correlation_matrix_dialog.generate_r_script()

    # Ambil hasil script
    script = correlation_matrix_dialog.script_box.toPlainText()

    # Validasi script
    for part in expected_parts:
        assert part in script

    # Kalau tidak ada yang diharapkan, pastikan script kosong
    if not expected_parts:
        assert script.strip() == ""
