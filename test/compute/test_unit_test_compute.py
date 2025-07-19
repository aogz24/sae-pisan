import polars as pl
from PyQt6.QtWidgets import QMessageBox

def get_data(parent):
    import os
    os.environ['R_HOME'] = f'F:\Kuliah\Skripsi\Aplikasi\sae-pisan\sip-sae\R\R-4.4.2'
    import rpy2.robjects as ro
    import rpy2_arrow.polars as rpy2polars
    df = parent.model.get_data()
    df.columns = [col.replace(' ', '_') for col in df.columns]
    
    null_threshold = 0.3 * len(df)
    cols_to_drop = [col for col in df.columns if df[col].null_count() >= null_threshold]
    if len(cols_to_drop)>0:
        df_pandas = df.to_pandas()
        df = pl.from_pandas(df_pandas)
    with rpy2polars.converter.context() as cv_ctx:
        r_df = cv_ctx.py2rpy(df)
        ro.globalenv['r_df'] = r_df

def get_script(self):
    return """
    new_column <- 1:nrow(data)
    """

def run_compute(self):
    import rpy2.robjects as ro
    get_data(self)
    try:
        ro.r('data <- as.data.frame(r_df)')
        ro.r("attach(data)")
        ro.r(get_script())
        new_column_name = self.column_name_input.text()
        new_column = ro.conversion.rpy2py(ro.globalenv['new_column'])
        ro.r("detach(data)")
        if new_column is not None:
            return pl.Series(new_column_name, list(new_column))
        QMessageBox.information(self, "Success", "New variable computed successfully!")
    except Exception as e:
        error_dialog = QMessageBox()
        error_dialog.setIcon(QMessageBox.Icon.Critical)
        error_dialog.setText("Error")
        error_dialog.setInformativeText(str(e))
        error_dialog.exec()
        return None
    
import pytest
import polars as pl
from PyQt6.QtWidgets import QMessageBox
from unittest.mock import MagicMock, patch

@pytest.fixture
def mock_parent():
    parent = MagicMock()
    parent.model.get_data.return_value = pl.DataFrame({
        'col 1': [1, 2, 3],
        'col 2': [4, 5, 6]
    })
    parent.column_name_input.text.return_value = 'new_col'
    return parent

@patch('compute.unit_test_compute.get_data')
@patch('compute.unit_test_compute.get_script', return_value="new_column <- 1:nrow(data)")
@patch('rpy2.robjects.r')
@patch('rpy2.robjects.conversion.rpy2py', return_value=[1, 2, 3])
def test_run_compute_success(mock_rpy2py, mock_r, mock_get_script, mock_get_data, mock_parent):
    result = run_compute(mock_parent)
    assert result is not None
    assert result.name == 'new_col'
    assert result.to_list() == [1, 2, 3]
    mock_r.assert_any_call('data <- as.data.frame(r_df)')
    mock_r.assert_any_call('attach(data)')
    mock_r.assert_any_call('detach(data)')

@patch('unit_test_compute.get_data')
@patch('unit_test_compute.get_script', return_value="new_column <- 1:nrow(data)")
@patch('rpy2.robjects.r')
@patch('rpy2.robjects.conversion.rpy2py', side_effect=Exception("Test Error"))
def test_run_compute_failure(mock_rpy2py, mock_r, mock_get_script, mock_get_data, mock_parent):
    with patch.object(QMessageBox, 'exec', return_value=None) as mock_exec:
        result = run_compute(mock_parent)
        assert result is None
        mock_exec.assert_called_once()
    