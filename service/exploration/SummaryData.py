import polars as pl
from PyQt6.QtWidgets import QMessageBox
from collections import defaultdict
import re

import rpy2.robjects as ro
import rpy2_arrow.polars as rpy2polars


def extract_formatted_single(r_output: str, r_script: str) -> pl.DataFrame:
    pattern = r'(?<=\(")(.*?)(?="\))'
    variable_name = re.search(pattern, r_script).group(0)
    mapping = {
        "Min.": "Minimum", 
        "1st Qu.": "Quartile 1",
        "Median": "Median",
        "Mean": "Mean",
        "3rd Qu.": "Quartile 3",
        "Max.": "Maximum"
    }

    lines = r_output.strip().split('\n')
    lines = [line.strip() for line in lines if line.strip()]

    data = {"Variable Name": [variable_name]}
    for line in lines[1:]:
        parts = line.split()
        stat = " ".join(parts[1:-1])
        value = float(parts[-1])
        label = mapping.get(stat, stat)
        data[label] = [value]
        
    return pl.DataFrame(data)

def extract_formatted_multiple(r_output: str) -> pl.DataFrame:
    # Clean up r_output and split into lines
    lines = r_output.strip().strip("[]").split('\n')
    lines = [line.strip(" '") for line in lines if line.strip()]

    # Regex pattern: find the number at the beginning, then the variable name, then the type of statistic, then the value
    pattern = r'^\d+\s+([A-Za-z0-9_.]+)\s+(Min\.|1st Qu\.|Median|Mean|3rd Qu\.|Max\.)\s*:\s*([-\d.]+)'
    
    summary_data = defaultdict(dict)
    
    # Mapping of R statistic names to desired labels
    stat_label_map = {
        "Min.": "Minimum",
        "1st Qu.": "Quartile 1",
        "Median": "Median",
        "Mean": "Mean",
        "3rd Qu.": "Quartile 3",
        "Max.": "Maximum"
    }

    # Original order of statistics from R
    stat_order_r = ["Min.", "1st Qu.", "Median", "Mean", "3rd Qu.", "Max."]

    # Create a dictionary to store the results
    result_dict = {"Variable Name": []}
    for r_stat in stat_order_r:
        label = stat_label_map[r_stat]
        result_dict[label] = []

    # Parsing the lines
    for line in lines:
        match = re.match(pattern, line)
        if match:
            var_name = match.group(1)
            stat_type = match.group(2)
            value = float(match.group(3))
            summary_data[var_name][stat_type] = value

    for var in summary_data:
        result_dict["Variable Name"].append(var)
        for r_stat in stat_order_r:
            label = stat_label_map[r_stat]
            result_dict[label].append(summary_data[var].get(r_stat, None))

    return pl.DataFrame(result_dict)

def run_summary_data(parent):
    """
    Run data summary using Python (Polars) and R.
    """
    parent.activate_R()  

    # Get data from model
    df1 = parent.model1.get_data()
    df2 = parent.model2.get_data()

    # Combine data using Polars
    df = pl.concat([df1, df2], how="horizontal")

    # Convert Polars DataFrame to R DataFrame
    with rpy2polars.converter.context() as cv_ctx:
        r_df = rpy2polars.converter.py2rpy(df)
        ro.globalenv['r_df'] = r_df

    try:
        # Set data in R
        ro.r('data <- as.data.frame(r_df)')
        
        # Execute R script from parent
        ro.r(parent.r_script)

        # Create summary_table in R
        ro.r('''
            if (is.matrix(summary_results)) {
                summary_table <- as.data.frame(summary_results)
            } else if (is.atomic(summary_results)) {
                summary_table <- data.frame(stat = names(summary_results), value = as.numeric(summary_results))
            }
        ''')

        # Get the number of rows and columns from the summary_table in R
        nrow = int(ro.r('nrow(summary_table)')[0])
        ncol = int(ro.r('ncol(summary_table)')[0])

        # Get the output summary_table as a string
        summary_str = ro.r('capture.output(print(summary_table))')
        summary_str_joined = "\n".join(summary_str)

        # Use the appropriate function
        if nrow == 6 and ncol == 2:
            summary_table = extract_formatted_single(summary_str_joined, parent.r_script)
        else:
            summary_table = extract_formatted_multiple(summary_str_joined)

        # Save to the result
        parent.result = {
            "Summary Table": summary_table
        }

    except Exception as e:
        parent.result = str(e)
        parent.error = True
