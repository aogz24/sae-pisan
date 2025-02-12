import pandas as pd

def convert_df(df, parent):
    import rpy2_arrow.polars as rpy2polars
    import rpy2.robjects as ro
    parent.activate_R()
    with rpy2polars.converter.context() as cv_ctx:
        r_df = rpy2polars.converter.py2rpy(df)
        ro.globalenv['r_df'] = r_df