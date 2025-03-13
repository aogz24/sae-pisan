import polars as pl
from PyQt6.QtWidgets import QMessageBox
from service.utils.convert import get_data

def run_compute(parent):
    """
    Executes an R script provided by the parent object and computes a new column.
    This function retrieves data from the parent object, converts it to an R dataframe,
    attaches the dataframe in the R environment, runs the R script provided by the parent,
    and extracts the newly computed column. If successful, it returns the new column as a
    Polars Series. If an error occurs, it displays an error message.
    Parameters:
    parent (object): The parent object containing the data and the R script to be executed.
                     It should have the methods `get_script()` and `column_name_input.text()`.
    Returns:
    pl.Series: A Polars Series containing the new column if computation is successful.
    None: If an error occurs during the computation.
    """
    
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
    