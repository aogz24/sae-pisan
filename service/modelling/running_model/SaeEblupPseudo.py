import polars as pl
from PyQt6.QtWidgets import QMessageBox
from service.modelling.running_model.convert_df import convert_df

def run_model_eblup_pseudo(parent):
    import rpy2.robjects as ro
    import rpy2_arrow.polars as rpy2polars
    parent.activate_R()
    df = parent.model1.get_data()
    df = df.drop_nulls()
    convert_df(df, parent)
    try:
        ro.r('suppressMessages(library("emdi"))')
        ro.r('data <- as.data.frame(r_df)')
        ro.r(parent.r_script)
        ro.r('estimated_value <- getResponse(model)\n mse <- model$MSE$FH \n domain<-model$MSE$Domain')
        domain = ro.conversion.rpy2py(ro.globalenv['domain'])
        result_str = ro.r('capture.output(print(model))')
        result = "\n".join(result_str)
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
        parent.result = str(result)
        
    except Exception as e:
        error_dialog = QMessageBox()
        error_dialog.setIcon(QMessageBox.Icon.Critical)
        error_dialog.setText("Error")
        error_dialog.setInformativeText(str(e))