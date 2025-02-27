import pytest
import sys
import polars as pl
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtCore import Qt  # Perbaikan untuk penggunaan Qt.MouseButton
from view.components.exploration.NormalityTestDialog import NormalityTestDialog
from unittest.mock import MagicMock, Mock

app = QApplication.instance()
if not app:
    app = QApplication(sys.argv)

@pytest.fixture
def normality_test_dialog(qtbot):
    parent = QWidget()
    dialog = NormalityTestDialog(parent)
    qtbot.addWidget(dialog)
    return dialog

# Test inisialisasi normality_test_dialog
def test_ui_initialization(normality_test_dialog):
    assert normality_test_dialog.windowTitle() == 'Normality Test'
    assert normality_test_dialog.shapiro_checkbox.text() == 'Shapiro-Wilk'
    assert normality_test_dialog.jarque_checkbox.text() == 'Jarque-Bera'
    assert normality_test_dialog.lilliefors_checkbox.text() == 'Lilliefors'
    assert normality_test_dialog.histogram_checkbox.text() == 'Histogram'
    assert normality_test_dialog.qqplot_checkbox.text() == 'Q-Q Plot'

# Test set_model() untuk mengisi daftar variabel
def test_set_model(normality_test_dialog):
    model1_mock = MagicMock()
    model2_mock = MagicMock()
    model1_mock.get_data.return_value.columns = ['var1', 'var2']
    model1_mock.get_data.return_value.dtypes = [pl.Int64, pl.Utf8]  # Perbaikan mapping tipe data
    model2_mock.get_data.return_value.columns = ['var3']
    model2_mock.get_data.return_value.dtypes = [pl.Int64]
    
    normality_test_dialog.set_model(model1_mock, model2_mock)
    
    expected_list_1 = ['var1 [Numeric]', 'var2 [String]']
    expected_list_2 = ['var3 [Numeric]']
    
    assert normality_test_dialog.data_editor_model.stringList() == expected_list_1
    assert normality_test_dialog.data_output_model.stringList() == expected_list_2

def test_get_column_with_dtype(normality_test_dialog):
    """Test if get_column_with_dtype returns the correct formatted column names."""
    mock_model = Mock()
    mock_model.get_data.return_value.columns = ["col1", "col2"]
    mock_model.get_data.return_value.dtypes = [pl.Float64, pl.Utf8]

    result = normality_test_dialog.get_column_with_dtype(mock_model)
    assert result == ["col1 [Numeric]", "col2 [String]"]

def test_add_variable(normality_test_dialog, qtbot):
    normality_test_dialog.data_editor_model.setStringList(['var1 [Numeric]', 'var2 [String]'])
    normality_test_dialog.data_output_model.setStringList(['var3 [Numeric]'])
    
    normality_test_dialog.data_editor_list.setCurrentIndex(normality_test_dialog.data_editor_model.index(0))
    normality_test_dialog.data_output_list.setCurrentIndex(normality_test_dialog.data_output_model.index(0))
    
    qtbot.mouseClick(normality_test_dialog.add_button, Qt.MouseButton.LeftButton)  # Perbaikan di sini
    assert 'var1 [Numeric]' in normality_test_dialog.selected_model.stringList()
    assert 'var3 [Numeric]' in normality_test_dialog.selected_model.stringList()
    assert 'var2 [String]' not in normality_test_dialog.selected_model.stringList()

def test_remove_variable(normality_test_dialog, qtbot):
    normality_test_dialog.selected_model.setStringList(['var1 [Numeric]', 'var3 [Numeric]'])
    
    normality_test_dialog.selected_list.setCurrentIndex(normality_test_dialog.selected_model.index(0))
    qtbot.mouseClick(normality_test_dialog.remove_button, Qt.MouseButton.LeftButton)  # Perbaikan di sini
    
    assert 'var1 [Numeric]' not in normality_test_dialog.selected_model.stringList()
    assert 'var3 [Numeric]' in normality_test_dialog.selected_model.stringList()

import pytest

@pytest.mark.parametrize(
    "selected_columns, shapiro, jarque, lilliefors, histogram, qqplot, expected_in_script, not_expected_in_script",
    [
        # Hanya Shapiro-Wilk dan Jarque-Bera
        (
            ["var1 [Numeric]", "var3 [Numeric]"], True, True, False, False, False,
            [
                "shapiro.test(data$var1)", "tseries::jarque.bera.test(data$var1)",
                "shapiro.test(data$var3)", "tseries::jarque.bera.test(data$var3)"
            ],
            [
                "nortest::lillie.test(data$var1)", "nortest::lillie.test(data$var3)",
                "ggplot(data, aes(x = var1))", "ggplot(data, aes(x = var3))"
            ]
        ),
        # Semua metode uji normalitas
        (
            ["var1 [Numeric]", "var3 [Numeric]"], True, True, True, False, False,
            [
                "shapiro.test(data$var1)", "tseries::jarque.bera.test(data$var1)", "nortest::lillie.test(data$var1)",
                "shapiro.test(data$var3)", "tseries::jarque.bera.test(data$var3)", "nortest::lillie.test(data$var3)"
            ],
            []
        ),
        # Histogram diaktifkan
        (
            ["var1 [Numeric]", "var3 [Numeric]"], True, True, True, True, False,
            [
                "ggplot(data, aes(x = var1))", "geom_histogram(binwidth = 30", "ggtitle('Histogram of var1')",
                "ggplot(data, aes(x = var3))", "ggtitle('Histogram of var3')"
            ],
            []
        ),
        # Q-Q Plot diaktifkan
        (
            ["var1 [Numeric]", "var3 [Numeric]"], True, True, True, True, True,
            [
                "ggtitle('Q-Q Plot of var1')", "stat_qq()", "stat_qq_line(color = 'red')",
                "ggtitle('Q-Q Plot of var3')"
            ],
            []
        ),
    ]
)
def test_generate_r_script(
    normality_test_dialog, selected_columns, shapiro, jarque, lilliefors, histogram, qqplot, expected_in_script, not_expected_in_script
):
    normality_test_dialog.selected_model.setStringList(selected_columns)
    normality_test_dialog.shapiro_checkbox.setChecked(shapiro)
    normality_test_dialog.jarque_checkbox.setChecked(jarque)
    normality_test_dialog.lilliefors_checkbox.setChecked(lilliefors)
    normality_test_dialog.histogram_checkbox.setChecked(histogram)
    normality_test_dialog.qqplot_checkbox.setChecked(qqplot)

    normality_test_dialog.generate_r_script()
    script_content = normality_test_dialog.script_box.toPlainText()

    for expected in expected_in_script:
        assert expected in script_content

    for not_expected in not_expected_in_script:
        assert not_expected not in script_content
