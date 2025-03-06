import polars as pl
from PyQt6.QtWidgets import QMessageBox
from service.modelling.running_model.convert_df import convert_df
from rpy2.rinterface_lib.embedded import RRuntimeError

def run_model_projection(parent):
    import rpy2.robjects as ro
    parent.activate_R()
    df = parent.model1.get_data()
    # df = df.drop_nulls()
    convert_df(df, parent)
    try:
        ro.r('suppressMessages(library(sae.projection))')
        ro.r('data <- as.data.frame(r_df)')
        try:
            ro.r(parent.r_script)  # Menjalankan skrip R
        
        except RRuntimeError as e:
            error_dialog = QMessageBox()
            error_dialog.setIcon(QMessageBox.Icon.Critical)
            error_dialog.setText("Error when run R")
            error_dialog.setInformativeText(str(e))
            error_dialog.exec()
            parent.result = str(e)
            parent.error = True
            return
        result_str = ro.r('capture.output(print(model))')
        result = "\n".join(result_str)
        parent.result = str(result)
        ro.r('projection <- model$projection')
        proj = ro.conversion.rpy2py(ro.globalenv['projection'])
        df = pl.from_pandas(proj)
        parent.model2.set_data(df)
        parent.error = False
        
    except Exception as e:
        error_dialog = QMessageBox()
        error_dialog.setIcon(QMessageBox.Icon.Critical)
        error_dialog.setText("Error")
        error_dialog.setInformativeText(str(e))