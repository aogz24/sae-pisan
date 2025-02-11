import polars as pl
from PyQt6.QtWidgets import QMessageBox

def run_model_projection(parent):
    import rpy2.robjects as ro
    import rpy2_arrow.polars as rpy2polars
    parent.activate_R()
    df = parent.model1.get_data()
    # df = df.drop_nulls()
    with rpy2polars.converter.context() as cv_ctx:
        r_df = rpy2polars.converter.py2rpy(df)
        ro.globalenv['r_df'] = r_df
    try:
        ro.r('suppressMessages(library(sae.projection))')
        ro.r('data <- as.data.frame(r_df)')
        ro.r(parent.r_script)
        ro.r("print(model)")
        result_str = ro.r('capture.output(print(model))')
        ro.r('projection <- model$projection')
        proj = ro.conversion.rpy2py(ro.r("projection"))
        result = "\n".join(result_str)
        df = pl.from_pandas(proj)
        parent.model2.set_data(df)
        parent.result = str(result)
        
    except Exception as e:
        error_dialog = QMessageBox()
        error_dialog.setIcon(QMessageBox.Icon.Critical)
        error_dialog.setText("Error")
        error_dialog.setInformativeText(str(e))