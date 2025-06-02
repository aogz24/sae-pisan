import polars as pl
import rpy2.robjects as ro
from rpy2.robjects import pandas2ri
import re
from service.utils.convert import get_data

# Aktifkan converter pandas <-> R
pandas2ri.activate()

def extract_formatted(r_output: str):
    lines = r_output.strip().split('\n')
    # print("Lines:", lines)
    call = ""
    residuals = []
    coef_lines = []
    summary_info = {}

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Call
        if line.startswith("Call:"):
            call = lines[i + 1].strip()
            i += 2
            continue

        # Residuals
        elif line.startswith("Residuals:"):
            i += 1
            while i < len(lines) and lines[i].strip():
                residuals.append(lines[i].strip())
                i += 1
            continue

        # Coefficients
        elif line.startswith("Coefficients:"):
            i += 1
            while i < len(lines) and not lines[i].startswith("---") and not lines[i].startswith("Signif. codes:"):
                coef_lines.append(lines[i].strip())
                i += 1
            continue

        # Residual std error
        elif "Residual standard error" in line:
            match = re.search(r"Residual standard error:\s+([\d.]+) on (\d+) degrees of freedom", line)
            if match:
                summary_info["Residual Std Error"] = float(match.group(1))
                summary_info["DF"] = int(match.group(2))

        # R-squared
        elif "Multiple R-squared" in line:
            match = re.search(r"Multiple R-squared:\s+([\d.]+),\s+Adjusted R-squared:\s+([\d.]+)", line)
            if match:
                summary_info["R-squared"] = float(match.group(1))
                summary_info["Adj R-squared"] = float(match.group(2))

        # F-statistic
        elif "F-statistic" in line:
            match = re.search(r"F-statistic:\s+([\d.]+) on (\d+) and (\d+) DF,\s+p-value:\s+([^\s]+)", line)
            if match:
                summary_info["F-statistic"] = float(match.group(1))
                summary_info["F DF1"] = int(match.group(2))
                summary_info["F DF2"] = int(match.group(3))
                summary_info["F p-value"] = match.group(4)

        i += 1

    def extract_residuals(residuals: list[str]) -> pl.DataFrame:
        labels = residuals[0].split()
        # Ubah nama kolom sesuai permintaan
        labels = [label.replace("Min", "Minimum").replace("1Q", "Quartile 1").replace("3Q", "Quartile 3").replace("Max", "Maximum") for label in labels]
        values = list(map(float, residuals[1].split()))
        return pl.DataFrame([dict(zip(labels, values))])
    
    residual_df = extract_residuals(residuals)


    def extract_coefficients(coef_lines: list[str]) -> pl.DataFrame:
        import re

        columns = ["Variable", "Estimate", "Std. Error", "t Value", "P-value", "Significance"]
        rows = []

        signif_map = {
            '***': "Significant at 0.1% level",
            '**': "Significant at 1% level",
            '*': "Significant at 5% level",
            '.': "significant at 10% level",
            '': "Not significant at 10% level"
        }

        for line in coef_lines[1:]:
            match = re.match(
                r"^(`[^`]+`|\S+)\s+"  
                r"([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?|\d+)\s+"
                r"([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?|\d+)\s+"
                r"([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?|\d+)\s+"
                r"([<>=]*\s*[\d.eE+-]+)\s*"
                r"(\*\*\*|\*\*|\*|\.|)?",
                line
            )
            if match:
                variable = match.group(1).strip('`')
                estimate = float(match.group(2))
                std_error = float(match.group(3))
                t_value = float(match.group(4))
                p_value = match.group(5).strip()
                signif_code = match.group(6).strip() if match.group(6) else ''
                significance = signif_map.get(signif_code, "Not significant")

                rows.append({
                    "Variable": variable,
                    "Estimate": estimate,
                    "Std. Error": std_error,
                    "t Value": t_value,
                    "P-value": p_value,
                    "Significance": significance
                })

        return pl.DataFrame(rows)
    coef_df = extract_coefficients(coef_lines)

    def summary_info_to_table(summary_info: dict) -> pl.DataFrame:
        """
        Convert summary info dictionary to a Polars DataFrame with float values.
        """
        return pl.DataFrame({
            "Description": list(summary_info.keys()),
            "Value": [float(v) for v in summary_info.values()]
        })

    summary_table = summary_info_to_table(summary_info)
    # print("Call:", call)
    # print("Residuals DataFrame:", residual_df)
    # print("Coefficients DataFrame:", coef_df)
    # print("Summary Table:", summary_table)

    return {
        "call": call,
        "residuals": residual_df,
        "coefficients": coef_df,
        "summary": summary_table,
    }

def run_variable_selection(parent):
    parent.activate_R()

    df1 = parent.model1.get_data()
    df2 = parent.model2.get_data()

    # Gabungkan dan filter data kosong
    df = pl.concat([df1, df2], how="horizontal")
    df = df.filter(~pl.all_horizontal(pl.all().is_null()))
    get_data(parent,df)

    try:
        ro.r('suppressMessages(library(car))')
        ro.r('rm(list=ls()[ls() != "r_df"])')
        ro.r('data <- as.data.frame(r_df)')

        # Jalankan R script dari parent
        ro.r(parent.r_script)

        result_dict = {}
        existing_objects = list(ro.r("ls()"))

        # Daftar metode seleksi variabel
        methods = ["forward", "backward", "both"]

        method_label_map = {
            "forward": "Forward",
            "backward": "Backward",
            "both": "Stepwise"
        }

        for method in methods:
            model_var = f"{method}_model"
            result_var = f"{method}_result"
            prefix = method_label_map[method]  


            if model_var in existing_objects:
                # 1. ANOVA Table
                try:
                    anova_r = ro.r(f"{model_var}$anova")
                    anova_pd = pandas2ri.rpy2py(anova_r)
                    if anova_pd.index.name and anova_pd.index.name not in anova_pd.columns:
                        anova_pd = anova_pd.reset_index()
                    if 'Step' in anova_pd.columns:
                        anova_pd['Step'] = anova_pd['Step'].astype(str).str.replace('`', '', regex=False)
                    result_dict[f"Anova {method.capitalize()} Selection"] = pl.from_pandas(anova_pd)
                except Exception as e:
                    result_dict[f"Anova {method.capitalize()} Selection"] = f"[ERROR] {e}"
            if result_var in existing_objects:
                try:
                    # Tangkap output summary sebagai string
                    summary_text = ro.r(f'capture.output(print({result_var}))')
                    summary_text_joined = "\n".join(summary_text)
                    # print(f"Summary Text for {method}:", summary_text_joined)
                    parsed = extract_formatted(summary_text_joined)

                    # Masukkan ke result_dict satu per satu dengan key terpisah
                    result_dict[f"Regression Model {prefix} Selection"] = parsed["call"]
                    result_dict[f"Residual {prefix} Selection"] = parsed["residuals"]
                    result_dict[f"Coefficients {prefix} Selection"] = parsed["coefficients"]
                    result_dict[f"Summary {prefix} Selection"] = parsed["summary"]

                except Exception as e:
                    result_dict[f"Regression Summary {prefix} Selection"] = f"[ERROR] {e}"

            parent.result = result_dict

    except Exception as e:
        parent.error = True
        parent.result = str(e)
        return
