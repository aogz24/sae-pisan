import polars as pl
from PyQt6.QtWidgets import QMessageBox
from service.modelling.running_model.convert_df import convert_df
from rpy2.rinterface_lib.embedded import RRuntimeError


def extract_output2_results(output):
    """
    Extracts results from the given output2 string and returns it as a dictionary.
    """
    import re

    # Extract formula
    formula_match = re.search(r"formula\s*=\s*(.+)", output)
    if formula_match:
        formula = formula_match.group(1).strip()
    else:
        formula = "No formula found"

    # Extract coefficients
    coefficients_match = re.search(r'Coefficients:\s+((?:.+\n)+)', output, re.S)
    if coefficients_match:
        coefficients = coefficients_match.group(1).strip()
        rows = coefficients.split('\n')
        
        # Process header and data rows
        header = rows[0].split()
        data = [row.split() for row in rows[1:] if row.strip()]
        
        # Ensure all rows have the same number of columns as the header
        max_columns = len(header)
        data = [row + [None] * (max_columns - len(row)) for row in data]
        
        # Convert to Polars DataFrame
        coeff = pl.DataFrame(data, schema=header, orient="row")
    else:
        coeff = pl.DataFrame()

    return formula, coeff

def run_model_projection(parent):
    """
    Runs the model projection using R scripts and returns the results.
    Parameters:
    parent (object): The parent object that contains the necessary methods and attributes for running the model projection.
    Returns:
    tuple: A tuple containing:
        - result (str): The result of the model projection or error message.
        - error (bool): A boolean indicating whether an error occurred.
        - df (polars.DataFrame or None): The projected data as a Polars DataFrame if successful, otherwise None.
    """
    
    import rpy2.robjects as ro
    parent.activate_R()
    df = parent.model1.get_data()
    # df = df.drop_nulls()
    convert_df(df, parent)
    result = ""
    error = False
    try:
        ro.r('data_pe <- as.data.frame(r_df)')
        try:
            ro.r(parent.r_script)  # Menjalankan skrip R
        except RRuntimeError as e:
            result = str(e)
            error = True
            return result, error, None
        ro.r('summary_pe <- model_pe$model \n pred_pe <-model_pe$prediction')
        summary = ro.globalenv['summary_pe']
        formula, coeff = extract_output2_results(str(summary))
        pred = ro.conversion.rpy2py(ro.globalenv['pred_pe'])
        pred = [float(value) for value in pred]
        pred_df = pl.DataFrame({
            "Index": range(1, len(pred) + 1),
            "Value": pred
        })
        results = {
            'Model': "Projection Estimation",
            'Formula of Modelling': formula,
            'Coefficients of Modelling': coeff,
            'Prediction': pred_df
        }
        ro.r('projection_pe <- model_pe$projection')
        proj = ro.conversion.rpy2py(ro.globalenv['projection_pe'])
        df = pl.from_pandas(proj)
        error = False
        return results, error, df
        
    except Exception as e:
        error = True
        return str(e), error, None