import polars as pl
class SaeModelling:
    def __init__(self, model1, model2, view):
        self.model1 = model1
        self.model2 = model2
        self.view = view
        
    def activateR(self):
        from rpy2.robjects import pandas2ri
        pandas2ri.activate()
        
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
            print(vardir_var)
            df = pl.DataFrame({
                'Estimated_Value': estimated_value,
                'Standar_Error': mse**0.5,
                'Varians Direct': vardir_var})
            print(df)
            self.model2.set_data(df)
        except Exception as e:
            print(e)
    
    def get_model2(self):
        return self.model2