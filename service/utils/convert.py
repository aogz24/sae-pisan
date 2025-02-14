def get_data(parent):
    import rpy2.robjects as ro
    import rpy2_arrow.polars as rpy2polars
    df = parent.model.get_data()
    df.columns = [col.replace(' ', '_') for col in df.columns]
    with rpy2polars.converter.context() as cv_ctx:
        r_df = cv_ctx.py2rpy(df)
        ro.globalenv['r_df'] = r_df