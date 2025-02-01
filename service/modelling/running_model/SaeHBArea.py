import polars as pl
from PyQt6.QtWidgets import QMessageBox

def run_model_hb_area(parent):
    import rpy2.robjects as ro
    import rpy2_arrow.polars as rpy2polars
    parent.activate_R()
    df = parent.model1.get_data()
    df = df.drop_nulls()
    with rpy2polars.converter.context() as cv_ctx:
        r_df = rpy2polars.converter.py2rpy(df)
        ro.globalenv['r_df'] = r_df
    try:
        ro.r('suppressMessages(library(saeHB))')
        ro.r('data <- as.data.frame(r_df)')
        ro.r(parent.r_script)
        ro.r('estimated_value <- model$Est')
        ro.r('print(class(estimated_value))')
        ro.r('sd <- model$sd')
        ro.r('refVar <- model$refVar')
        ro.r('coefficient <- model$coefficient')
        
        result_str = "Estimated Value:\n" + "\n".join(ro.r('capture.output(print(estimated_value))')) + "\n\n"
        result_str += "Standard Deviation:\n" + "\n".join(ro.r('capture.output(print(sd))')) + "\n\n"
        result_str += "Reference Variance:\n" + "\n".join(ro.r('capture.output(print(refVar))')) + "\n\n"
        result_str += "Coefficient:\n" + "\n".join(ro.r('capture.output(print(coefficient))')) + "\n"
        parent.result = result_str
        estimated_value = ro.conversion.rpy2py(ro.globalenv['estimated_value'])
        mse = ro.conversion.rpy2py(ro.globalenv['sd'])
        df = pl.DataFrame({
            'HB': estimated_value,
            'SD': mse,})
        parent.model2.set_data(df)
        
    except Exception as e:
        error_dialog = QMessageBox()
        error_dialog.setIcon(QMessageBox.Icon.Critical)
        error_dialog.setText("Error")
        error_dialog.setInformativeText(str(e))