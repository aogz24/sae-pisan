import polars as pl
from PyQt6.QtWidgets import QMessageBox
from service.utils.convert import get_data

def run_compute(parent):
    import rpy2.robjects as ro
    get_data(parent)
    try:
        ro.r('data <- as.data.frame(r_df)')
        ro.r("attach(data)")
        ro.r(parent.get_script())
        new_column_name = parent.column_name_input.text()
        new_column = ro.conversion.rpy2py(ro.globalenv['new_column'])
        ro.r("detach(data)")
        if new_column is not None:
            return pl.Series(new_column_name, list(new_column))
        QMessageBox.information(parent, "Success", "New variable computed successfully!")
    except Exception as e:
        error_dialog = QMessageBox()
        error_dialog.setIcon(QMessageBox.Icon.Critical)
        error_dialog.setText("Error")
        error_dialog.setInformativeText(str(e))
        error_dialog.exec()
        return None
    