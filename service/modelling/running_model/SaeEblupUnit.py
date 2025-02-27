import polars as pl
from PyQt6.QtWidgets import QMessageBox
from service.modelling.running_model.convert_df import convert_df
from rpy2.rinterface_lib.embedded import RRuntimeError

def run_model_eblup_unit(parent):
    import rpy2.robjects as ro
    parent.activate_R()
    df = parent.model1.get_data()
    df = df.drop_nulls()
    convert_df(df, parent)
    try:
        ro.r('suppressMessages(library(sae))')
        ro.r('data <- as.data.frame(r_df)')
        try:
            ro.r(parent.r_script)  # Menjalankan skrip R
            ro.r("print(model)")   # Mencetak model di R
        except RRuntimeError as e:
            error_dialog = QMessageBox()
            error_dialog.setIcon(QMessageBox.Icon.Critical)
            error_dialog.setText("Error when run R")
            error_dialog.setInformativeText(str(e))
            error_dialog.exec()
            parent.result = str(e)
            parent,error = str(e)
        ro.r('domain <- model$est$eblup$domain\n estimated_value <- model$est$eblup$eblup\n n_size <- model$est$eblup$sampsize \n mse <- model$mse$mse')
        result_str = ro.r('capture.output(print(model))')
        result = "\n".join(result_str)
        parent.result = str(result)
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
        
    except Exception as e:
        error_dialog = QMessageBox()
        error_dialog.setIcon(QMessageBox.Icon.Critical)
        error_dialog.setText("Error")
        error_dialog.setInformativeText(str(e))