import polars as pl
from PyQt6.QtWidgets import QMessageBox
from service.modelling.running_model.convert_df import convert_df

def run_model_projection(parent):
    import rpy2.robjects as ro
    parent.activate_R()
    df = parent.model1.get_data()
    # df = df.drop_nulls()
    convert_df(df, parent)
    try:
        ro.r('suppressMessages(library(sae.projection))')
        ro.r('data <- as.data.frame(r_df)')
        ro.r(parent.r_script)
        ro.r("print(model)")
        result_str = ro.r('capture.output(print(model))')
        parent.result = str(result)
        ro.r('projection <- model$projection')
        proj = ro.conversion.rpy2py(ro.r("projection"))
        result = "\n".join(result_str)
        df = pl.from_pandas(proj)
        parent.model2.set_data(df)
        
    except Exception as e:
        error_dialog = QMessageBox()
        error_dialog.setIcon(QMessageBox.Icon.Critical)
        error_dialog.setText("Error")
        error_dialog.setInformativeText(str(e))