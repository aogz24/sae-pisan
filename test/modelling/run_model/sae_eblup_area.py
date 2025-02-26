import polars as pl
from PyQt6.QtWidgets import QMessageBox
from convert_df import convert_df

def run_model_eblup_area(parent):
    df = parent.model1.get_data()
    df = df.drop_nulls()
    try:
        estimated_value = [1, 2, 3]
        mse = [0.1, 0.2, 0.3]
        vardir_var = [0.1, 0.2, 0.3]
        result = "Dummy model result"

        rse = [m**0.5/e*100 for m, e in zip(mse, estimated_value)]
        df = pl.DataFrame({
            'Eblup': estimated_value,
            'MSE': mse,
            'RSE (%)': rse})
        parent.model2.set_data(df)
        parent.result = result
        
    except Exception as e:
        error_dialog = QMessageBox()
        error_dialog.setIcon(QMessageBox.Icon.Critical)
        error_dialog.setText("Error")
        error_dialog.setInformativeText(str(e))

import unittest
from unittest.mock import MagicMock, patch

class TestRunModelEblupArea(unittest.TestCase):

    @patch('sae_eblup_area.convert_df')
    @patch('sae_eblup_area.pl.DataFrame')
    @patch('sae_eblup_area.QMessageBox')
    def test_run_model_eblup_area_success(self, mock_QMessageBox, mock_DataFrame, mock_convert_df):
        mock_QMessageBox.return_value = MagicMock()
        parent = MagicMock()
        parent.model1.get_data.return_value.drop_nulls.return_value = 'mocked_df'
        parent.r_script = 'mocked_r_script'
        
        # Call the function
        run_model_eblup_area(parent)
        
        # Assertions
        parent.model1.get_data.assert_called_once()
        mock_DataFrame.assert_called_once_with({
            'Eblup': [1, 2, 3],
            'MSE': [0.1, 0.2, 0.3],
            'RSE (%)': [31.622776601683793, 22.360679774997898, 18.257418583505537]
        })
        parent.model2.set_data.assert_called_once_with(mock_DataFrame())
        self.assertEqual(parent.result, "Dummy model result")

if __name__ == '__main__':
    unittest.main()
