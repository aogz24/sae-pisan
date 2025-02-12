import polars as pl
from PyQt6.QtWidgets import QMessageBox

def run_compute(parent):
    import rpy2.robjects as ro
    import rpy2_arrow.polars as rpy2polars
    df = parent.model.get_data()
    df.columns = [col.replace(' ', '_') for col in df.columns]
    with rpy2polars.converter.context() as cv_ctx:
        r_df = rpy2polars.converter.py2rpy(df)
        ro.globalenv['r_df'] = r_df
    try:
        ro.r('data <- as.data.frame(r_df)')
        ro.r("attach(data)")
        ro.r(parent.get_script())
        new_column_name = parent.column_name_input.text()
        new_column = ro.conversion.rpy2py(ro.globalenv['new_column'])
        ro.r("detach(data)")
        QMessageBox.information(parent, "Success", "New variable computed successfully!")
        if new_column is not None:
            return pl.Series(new_column_name, list(new_column))
    except Exception as e:
        error_dialog = QMessageBox()
        error_dialog.setIcon(QMessageBox.Icon.Critical)
        error_dialog.setText("Error")
        error_dialog.setInformativeText(str(e))
        error_dialog.exec()
        return None
    