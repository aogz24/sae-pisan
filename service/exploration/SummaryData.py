import polars as pl
from PyQt6.QtWidgets import QMessageBox
from collections import defaultdict
import re

import rpy2.robjects as ro
import rpy2_arrow.polars as rpy2polars


def extract_formatted_single(r_output: str, r_script: str) -> pl.DataFrame:
    # Ambil nama variabel dari script R
    pattern = r'(?<=\(")(.*?)(?="\))'
    variable_name = re.search(pattern, r_script).group(0)

    # Mapping label
    mapping = {
        "Min.": "Minimum", 
        "1st Qu.": "Quartile 1",
        "Median": "Median",
        "Mean": "Mean",
        "3rd Qu.": "Quartile 3",
        "Max.": "Maximum",
        "Length": "Length",
        "Class": "Class",
        "Mode": "Mode"
    }

    lines = r_output.strip().split('\n')
    lines = [line.strip() for line in lines if line.strip()]

    data = {"Variable Name": [variable_name]}
    for line in lines[1:]:
        parts = line.split()
        if len(parts) == 3:  
            stat = parts[1]
            value = parts[2]
        else: 
            stat = " ".join(parts[1:-1])
            value = parts[-1]

        label = mapping.get(stat, stat)

        try:
            value = float(value)
        except ValueError:
            pass

        data[label] = [value]

    return pl.DataFrame(data)

def extract_summary(r_output: str) -> tuple[pl.DataFrame, pl.DataFrame]:
    # Clean r_output and split into lines
    lines = r_output.strip().strip("[]").split('\n')
    lines = [line.strip(" '") for line in lines if line.strip()]

    # Regex for numeric summary (Min., 1st Qu., ..., Max.)
    pattern_num = r'^\d+\s+([A-Za-z0-9_.\s]+)\s+(Min\.|1st Qu\.|Median|Mean|3rd Qu\.|Max\.)\s*:\s*([-\d.]+)'
    
    # Regex for string summary (Length, Class, Mode)
    pattern_char = r'^\d+\s+([A-Za-z0-9_.\s]+)\s+(Length|Class|Mode)\s*:\s*(.*)'

    stat_label_map = {
        "Min.": "Minimum",
        "1st Qu.": "Quartil 1",
        "Median": "Median",
        "Mean": "Mean",
        "3rd Qu.": "Quartil 3",
        "Max.": "Maximum"
    }

    stat_order = ["Min.", "1st Qu.", "Median", "Mean", "3rd Qu.", "Max."]
    string_keys = ["Length", "Class", "Mode"]

    # Save summary results
    numeric_summary = defaultdict(dict)
    string_summary = defaultdict(dict)

    for line in lines:
        if match := re.match(pattern_num, line):
            var_name = match.group(1).strip()
            stat = match.group(2)
            value = float(match.group(3))
            numeric_summary[var_name][stat] = value
        elif match := re.match(pattern_char, line):
            var_name = match.group(1).strip()
            stat = match.group(2)
            value = match.group(3).strip()
            string_summary[var_name][stat] = value

    # Create numeric DataFrame
    num_result = {
        "Variable Name": [],
        "Minimum": [],
        "Quartil 1": [],
        "Median": [],
        "Mean": [],
        "Quartil 3": [],
        "Maximum": []
    }

    for var in numeric_summary:
        num_result["Variable Name"].append(var)
        for stat in stat_order:
            num_result[stat_label_map[stat]].append(numeric_summary[var].get(stat, None))

    # Create string DataFrame
    char_result = {
        "Variable Name": [],
        "Length": [],
        "Class": [],
        "Mode": []
    }

    for var in string_summary:
        char_result["Variable Name"].append(var)
        for key in string_keys:
            char_result[key].append(string_summary[var].get(key, None))

    return pl.DataFrame(num_result), pl.DataFrame(char_result)

def extract_formatted_single(r_output: str, r_script: str) -> pl.DataFrame:
    # Ambil nama variabel dari script R
    pattern = r'(?<=\(")(.*?)(?="\))'
    variable_name = re.search(pattern, r_script).group(0)

    # Mapping label
    mapping = {
        "Min.": "Minimum", 
        "1st Qu.": "Quartile 1",
        "Median": "Median",
        "Mean": "Mean",
        "3rd Qu.": "Quartile 3",
        "Max.": "Maximum",
        "Length": "Length",
        "Class": "Class",
        "Mode": "Mode"
    }

    # Bersihkan dan pecah baris
    lines = r_output.strip().split('\n')
    lines = [line.strip() for line in lines if line.strip()]

    # Inisialisasi dictionary dengan kolom Variable Name
    data = {"Variable Name": [variable_name]}

    # Proses setiap baris statistik
    for line in lines[1:]:
        parts = line.split()
        if len(parts) == 3:  # Untuk string seperti: 1 Length 100
            stat = parts[1]
            value = parts[2]
        else:  # Untuk numerik: 1 Min. 4.166667
            stat = " ".join(parts[1:-1])
            value = parts[-1]

        label = mapping.get(stat, stat)

        # Coba ubah ke float, jika gagal tetap string
        try:
            value = float(value)
        except ValueError:
            pass

        data[label] = [value]

    return pl.DataFrame(data)

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

        parent.result = {}

        # Jika row ≤ 6 anggap sebagai single summary (numeric atau string)
        if nrow <= 6:
            summary_table = extract_formatted_single(summary_str_joined, parent.r_script)
            parent.result["Summary Table"] = summary_table
        else:
            # Gunakan extract_summary untuk data multi variabel
            numeric_df, string_df = extract_summary(summary_str_joined)

            if numeric_df.shape[0] > 0:
                parent.result["Summary Table (Numeric)"] = numeric_df
            if string_df.shape[0] > 0:
                parent.result["Summary Table (Character)"] = string_df

    except Exception as e:
        parent.result = str(e)
        parent.error = True
