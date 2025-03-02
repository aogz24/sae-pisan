import polars as pl
from PyQt6.QtWidgets import QMessageBox
from rpy2.rinterface_lib.embedded import RRuntimeError
from service.modelling.running_model.convert_df import convert_df

def run_model_eblup_pseudo(parent):
    import rpy2.robjects as ro
    parent.activate_R()
    df = parent.model1.get_data()
    df = df.drop_nulls()
    convert_df(df, parent)
    try:
        ro.r('suppressMessages(library("emdi"))')
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
            parent.error = True
            return
        ro.r('estimated_value <- getResponse(model)\n mse <- model$MSE$FH \n domain<-model$MSE$Domain')
        domain = ro.conversion.rpy2py(ro.globalenv['domain'])
        result_str = ro.r('capture.output(print(model))')
        result = "\n".join(result_str)
        parent.result = str(result)
        estimated_value = ro.conversion.rpy2py(ro.globalenv['estimated_value'])
        mse = ro.conversion.rpy2py(ro.globalenv['mse'])
        vardir_var = ro.conversion.rpy2py(ro.globalenv['vardir_var'])
        estimated_value = estimated_value.flatten()
        vardir_var = vardir_var.to_numpy()[:, 0]
        rse = mse**0.5/estimated_value*100
        df = pl.DataFrame({
            'Domain': domain,
            'Eblup': estimated_value,
            'MSE': mse,
            'RSE (%)': rse})
        parent.model2.set_data(df)
        
    except Exception as e:
        error_dialog = QMessageBox()
        error_dialog.setIcon(QMessageBox.Icon.Critical)
        error_dialog.setText("Error")
        error_dialog.setInformativeText(str(e))