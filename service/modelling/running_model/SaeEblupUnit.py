import polars as pl
from PyQt6.QtWidgets import QMessageBox
from service.modelling.running_model.convert_df import convert_df
from rpy2.rinterface_lib.embedded import RRuntimeError

def extract_formatted(output):
    import re
    # Fungsi untuk mengekstrak metode
    def extract_method(output):
        match = re.search(r'Linear mixed model fit by (.*?)\s+(\[.*?\])', output)
        return f"Linear mixed model fit by {match.group(1).strip()} {match.group(2).strip()}" if match else None

    # Fungsi untuk mengekstrak formula
    def extract_formula(output):
        match = re.search(r'Formula:\s+(.*?)\s+REML criterion', output)
        return match.group(1).strip() if match else None

    # Fungsi untuk mengekstrak metode dan kriterianya
    def extract_criterion(output):
        match = re.search(r'criterion at convergence:\s+([\d.-]+)', output)
        return float(match.group(1)) if match else None

    # Fungsi untuk mengekstrak jumlah observasi
    def number_of_obs(output):
        match = re.search(r'Number of obs:\s+(\d+)', output)
        return int(match.group(1)) if match else None

    # Fungsi untuk mengekstrak kelompok
    def extract_groups(output):
        match = re.search(r'Number of obs:\s+(\d+),\s+groups:\s+(.*?),\s+(\d+)', output)
        return f"Number of obs: {match.group(1)}, groups: {match.group(2)}, {match.group(3)}" if match else None

    # Fungsi untuk mengekstrak dataframe antara Scaled residuals dan Random effects
    def extract_summary(output):
        match = re.search(r'Scaled residuals:\s+(.*?)\s+Random effects:', output, re.S)
        if match:
            dataframe = match.group(1).strip()
            rows = dataframe.split('\n')
            data = [row.split(maxsplit=5) for row in rows if row.strip()]
            max_columns = 4
            data = [row + [None] * (max_columns - len(row)) for row in data]
            df = pl.DataFrame(data, schema=["Statistic", "Value"])
            df = df.with_columns([
                    pl.col("Statistic").replace(
                        ["Min", "1Q", "Median", "3Q", "Max"],
                        ["Minimum", "Quartil 1", "Median", "Quartil 3", "Maximum"]
                    ).alias("Statistic"),
                    pl.col("Value").cast(pl.Float64).alias("Value")
                ])
            return df
        return None

    # Fungsi untuk mengekstrak bagian Fixed effects
    def extract_fixed_effects(output):
        match = re.search(r'Fixed effects:\s+(.*?)\s+Correlation of Fixed Effects:', output, re.S)
        if match:
            dataframe = match.group(1).strip()
            rows = dataframe.split('\n')
            data = [row.split(maxsplit=4) for row in rows[1:] if row.strip()]
            df = pl.DataFrame(data, schema=["Effect", "Estimate", "Standard Error", "t-value"], orient="row")
            return df.with_columns([
                pl.col("Estimate").cast(pl.Float64).alias("Estimate"),
                pl.col("Standard Error").cast(pl.Float64).alias("Standard Error"),
                pl.col("t-value").cast(pl.Float64).alias("t-value")
            ])
        return None

    # Fungsi untuk mengekstrak bagian Random effects
    def extract_random_effects(output):
        match = re.search(r'Random effects:\s+(.*?)\s+Number of obs:', output, re.S)
        if match:
            dataframe = match.group(1).strip()
            rows = dataframe.split('\n')
            data = []
            for row in rows[1:]:
                if row.strip():
                    parts = row.split()
                    if len(parts) >= 4:
                        group, name, variance, std_dev = parts[0], parts[1], parts[-2], parts[-1]
                    else:
                        group, name, variance, std_dev = parts[0], None, parts[-2], parts[-1]
                    data.append([group, name, float(variance), float(std_dev)])
            return pl.DataFrame(data, schema=["Group", "Name", "Variance", "Standard Deviation"], orient="row")
        return None

    # Fungsi untuk mengekstrak bagian Correlation of Fixed Effects
    def correlation_fixed_effects(output):
        match = re.search(r'Correlation of Fixed Effects:\s+(.*?)\s+boundary', output, re.S)
        if match:
            dataframe = match.group(1).strip()
            rows = dataframe.split('\n')
            data = [row.split() for row in rows if row.strip()]
            data[0].insert(0, '')
            header = data[0]
            data = data[1:]
            max_columns = len(header)
            data = [row + [None] * (max_columns - len(row)) for row in data]
            return pl.DataFrame(data, schema=header, orient="row")
        return None

    # Menggabungkan hasil ekstraksi menjadi string yang user-friendly
    results = {
        "method": extract_method(output),
        "formula": extract_formula(output),
        "criterion": extract_criterion(output),
        "number_of_obs": number_of_obs(output),
        "groups": extract_groups(output),
        "summary": extract_summary(output),
        "fixed_effects": extract_fixed_effects(output),
        "random_effects": extract_random_effects(output),
        "correlation_fixed_effects": correlation_fixed_effects(output)
    }
    return results

def run_model_eblup_unit(parent):
    """
    Runs the EBLUP (Empirical Best Linear Unbiased Prediction) model using R through rpy2.
    Parameters:
    parent (object): An object that contains the necessary methods and attributes to run the model.
                     It should have the following methods and attributes:
                     - activate_R(): Method to activate the R environment.
                     - model1.get_data(): Method to get the data for the model.
                     - r_script: An R script to be executed.
    Returns:
    tuple: A tuple containing:
           - result (str): The result of the model execution or error message.
           - error (bool): A flag indicating whether an error occurred.
           - df (polars.DataFrame or None): A DataFrame containing the model results with columns 'Domain', 'Eblup', 'Sample size', and 'MSE'.
                                            None if an error occurred.
    """
    
    import rpy2.robjects as ro
    parent.activate_R()
    df = parent.model1.get_data()
    df = df.drop_nulls()
    convert_df(df, parent)
    result = ""
    error = False
    try:
        ro.r('suppressMessages(library(sae))')
        ro.r('data <- as.data.frame(r_df)')
        try:
            ro.r(parent.r_script)  # Menjalankan skrip R
        except RRuntimeError as e:
            result = str(e)
            error = True
            return result, error, None
        ro.r('domain <- model$est$eblup$domain\n estimated_value <- model$est$eblup$eblup\n n_size <- model$est$eblup$sampsize \n mse <- model$mse$mse')
        result_str = ro.r('model$est$fit$summary')
        result = str(result_str)
        results = extract_formatted(result)
        print(results)
        domain = ro.r('domain')
        estimated_value = ro.r('estimated_value')
        n_size = ro.r('n_size')
        mse = ro.r('mse')
        df = pl.DataFrame({
            'Domain': domain,
            'Eblup': estimated_value,
            'Sample size': n_size,
            'MSE': mse})
        error = False
        return results, error, df
        
    except Exception as e:
        error = True
        return str(e), error, None