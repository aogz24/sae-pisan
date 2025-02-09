import polars as pl
from PyQt6.QtWidgets import QMessageBox

def run_model_eblup_unit(parent):
    import rpy2.robjects as ro
    import rpy2_arrow.polars as rpy2polars
    parent.activate_R()
    df = parent.model1.get_data()
    df = df.drop_nulls()
    with rpy2polars.converter.context() as cv_ctx:
        r_df = rpy2polars.converter.py2rpy(df)
        ro.globalenv['r_df'] = r_df
    try:
        ro.r('suppressMessages(library(sae))')
        ro.r('data <- as.data.frame(r_df)')
        ro.r(parent.r_script)
        ro.r("print(model)")
        ro.r('domain <- model$est$eblup$domain\n estimated_value <- model$est$eblup$eblup\n n_size <- model$est$eblup$sampsize \n mse <- model$mse$mse')
        result_str = ro.r('capture.output(print(model))')
        result = "\n".join(result_str)
        domain = ro.r('domain')
        estimated_value = ro.r('estimated_value')
        n_size = ro.r('n_size')
        mse = ro.r('mse')
        df = pl.DataFrame({
            'Domain': domain,
            'Eblup': estimated_value,
            'Sample size': n_size,
            'MSE': mse})
        parent.model2.set_data(df)
        parent.result = str(result)
        
    except Exception as e:
        error_dialog = QMessageBox()
        error_dialog.setIcon(QMessageBox.Icon.Critical)
        error_dialog.setText("Error")
        error_dialog.setInformativeText(str(e))