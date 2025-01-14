from model.SaeModelling import SaeModelling
import polars as pl
from PyQt6.QtWidgets import QMessageBox

class SaeEblup(SaeModelling):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def RunModel(self, r_script):
        import rpy2.robjects as ro
        import rpy2_arrow.polars as rpy2polars
        self.activateR()
        df = self.model1.get_data()
        df = df.drop_nulls()
        with rpy2polars.converter.context() as cv_ctx:
            r_df = rpy2polars.converter.py2rpy(df)
            ro.globalenv['r_df'] = r_df
        try:
            ro.r('suppressMessages(library(sae))')
            ro.r('data <- as.data.frame(r_df)')
            ro.r(r_script)
            ro.r('estimated_value <- model$est$eblup\n mse <- model$mse')
            estimated_value = ro.conversion.rpy2py(ro.globalenv['estimated_value'])
            mse = ro.conversion.rpy2py(ro.globalenv['mse'])
            vardir_var = ro.conversion.rpy2py(ro.globalenv['vardir_var'])
            estimated_value = estimated_value.flatten()
            vardir_var = vardir_var.to_numpy()[:, 0]
            rse = mse**0.5/estimated_value*100
            df = pl.DataFrame({
                'Estimated Value': estimated_value,
                'Mean Square Error(%)': mse,
                'Relative Standar Error': rse,
                'Varians Direct': vardir_var})
            self.model2.set_data(df)
        except Exception as e:
            error_dialog = QMessageBox()
            error_dialog.setIcon(QMessageBox.Icon.Critical)
            error_dialog.setText("Error")
            error_dialog.setInformativeText(str(e))
    
    def get_model2(self):
        return self.model2