import polars as pl
import pandas as pd

def get_data(parent, df=None):
    """
    Retrieves data from the parent model or uses the provided dataframe, processes it, and converts it to an R dataframe.
    Args:
        parent: An object that contains a model with a `get_data` method.
        df: A pandas dataframe to be used instead of retrieving data from the parent model. Default is None.
    Returns:
        None. The resulting R dataframe is stored in the R global environment as 'r_df'.
    Process:
        1. Imports necessary modules from `rpy2` and `rpy2_arrow.polars`.
        2. Retrieves data from the parent model or uses the provided dataframe.
        3. Replaces spaces in column names with underscores.
        4. Drops columns with a high percentage of null values (threshold: 30%).
        5. Converts the dataframe to a pandas dataframe if columns are dropped.
        6. Converts the pandas dataframe to a polars dataframe.
        7. Converts the polars dataframe to an R dataframe and assigns it to the R global environment.
    """
    
    import rpy2.robjects as ro
    import rpy2_arrow.polars as rpy2polars
    
    if df is None:
        df = parent.model.get_data()
    
    null_threshold = 0.3 * len(df)
    cols_to_drop = [col for col in df.columns if df[col].null_count() >= null_threshold]
    if len(cols_to_drop) > 0:
        df_pandas = df.to_pandas()
        df = pl.from_pandas(df_pandas)
    with rpy2polars.converter.context() as cv_ctx:
        r_df = cv_ctx.py2rpy(df)
        ro.globalenv['r_df'] = r_df