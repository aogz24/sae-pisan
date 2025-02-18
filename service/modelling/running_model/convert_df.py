import polars as pl
def convert_df(df, parent):
    import rpy2_arrow.polars as rpy2polars
    import rpy2.robjects as ro
    parent.activate_R()
    
    null_threshold = 0.3 * len(df)
    cols_to_drop = [col for col in df.columns if df[col].null_count() >= null_threshold]
    if len(cols_to_drop)>0:
        df_pandas = df.to_pandas()
        df = pl.from_pandas(df_pandas)
    
    with rpy2polars.converter.context() as cv_ctx:
        r_df = cv_ctx.py2rpy(df)
        ro.globalenv['r_df'] = r_df