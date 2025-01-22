import polars as pl
from PyQt6.QtWidgets import QMessageBox

def run_model_hb_area(parent):
    import rpy2.robjects as ro
    import rpy2_arrow.polars as rpy2polars
    parent.activate_R()
    df = parent.model1.get_data()
    df = df.drop_nulls()
    with rpy2polars.converter.context():
        r_df = rpy2polars.converter.py2rpy(df)
        ro.globalenv['r_df'] = r_df
    try:
        ro.r('library(saeHB)')
        ro.r('data <- as.data.frame(r_df)')
        ro.r(parent.r_script)
        ro.r("estimated_value<-model$Est")
        # result_str = ro.r('print(model)')
        result = "\n"
        estimated_value = ro.conversion.rpy2py(ro.globalenv['estimated_value'])
        vardir_var = ro.conversion.rpy2py(ro.globalenv['vardir_var'])
        estimated_value = estimated_value.flatten()
        vardir_var = vardir_var.to_numpy()[:, 0]
        rse = vardir_var**0.5/estimated_value*100
        df = pl.DataFrame({
            'Estimated Value': estimated_value,
            'Relative Standar Error': rse,
            'Varians Direct': vardir_var})
        if df is None or df.shape[0] == 0:
            raise ValueError("Error when running model")
        parent.model2.set_data(df)
        parent.result = str(result)
        
    except Exception as e:
        error_dialog = QMessageBox()
        error_dialog.setIcon(QMessageBox.Icon.Critical)
        error_dialog.setText("Error")
        error_dialog.setInformativeText(str(e))