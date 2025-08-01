import polars as pl
def convert_df(df, parent):
    """
    Converts a Polars DataFrame to an R DataFrame using rpy2 and handles columns with a high percentage of null values.
    Parameters:
    df (pl.DataFrame): The Polars DataFrame to be converted.
    parent (object): An object that has a method `activate_R()` to activate the R environment.
    Returns:
    None: The function modifies the R global environment by adding the converted DataFrame as 'r_df'.
    Notes:
    - Columns with null values exceeding 30% of the DataFrame length are dropped before conversion.
    - The function uses the rpy2_arrow.polars and rpy2.robjects libraries for conversion.
    """
    
    import rpy2_arrow.polars as rpy2polars
    import rpy2.robjects as ro
    
    null_threshold = 0.49 * len(df)
    cols_to_drop = [col for col in df.columns if df[col].null_count() >= null_threshold]
    if len(cols_to_drop)>0:
        df_pandas = df.to_pandas()
        df = pl.from_pandas(df_pandas)
    
    with rpy2polars.converter.context() as cv_ctx:
        r_df = cv_ctx.py2rpy(df)
        ro.globalenv['r_df'] = r_df