import re
import polars as pl

# Mengubah r_output
r_output = """
Linear mixed model fit by REML ['lmerMod']
Formula: ys ~ -1 + Xs + (1 | dom)

REML criterion at convergence: 322

Scaled residuals: 
    Min      1Q  Median      3Q     Max 
-2.9288 -0.5711  0.1041  0.5953  1.5333 

Random effects:
 Groups   Name        Variance Std.Dev.
 dom      (Intercept)  63.31    7.957  
 Residual             297.71   17.254  
Number of obs: 37, groups:  dom, 12

Fixed effects:
                Estimate Std. Error t value
XsXs(Intercept) 17.96398   30.97450   0.580
XsXsCornPix      0.36634    0.06496   5.640
XsXsSoyBeansPix -0.03036    0.06758  -0.449

Correlation of Fixed Effects:
            XsX(I) XsXsCP
XsXsCornPix -0.947       
XsXsSyBnsPx -0.897  0.734 
boundary (singular) fit: see hel
"""

def extract_formatted(output):
    # Fungsi untuk mengekstrak metode
    def extract_method(output):
        match = re.search(r'Linear mixed model fit by (.*?)\s+(\[.*?\])', output)
        return {"method": match.group(1).strip(), "details": match.group(2).strip()} if match else None

    # Fungsi untuk mengekstrak formula
    def extract_formula(output):
        match = re.search(r'Formula:\s+(.*?)\s+REML criterion', output)
        return match.group(1).strip() if match else None

    # Fungsi untuk mengekstrak metode dan kriterianya
    def extract_criterion(output):
        match = re.search(r'Linear mixed model fit by (.*?)\s+\[.*?\]\s+.*?criterion at convergence:\s+([\d.-]+)', output, re.S)
        return {"method": match.group(1).strip(), "criterion": int(match.group(2))} if match else None

    # Fungsi untuk mengekstrak jumlah observasi
    def number_of_obs(output):
        match = re.search(r'Number of obs:\s+(\d+)', output)
        return int(match.group(1)) if match else None

    # Fungsi untuk mengekstrak kelompok
    def extract_groups(output):
        match = re.search(r'groups:\s+(.*?),\s+(\d+)', output)
        return {"group name": match.group(1).strip(), "group count": int(match.group(2))} if match else None

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

    formatted = []

    if results["method"]:
        formatted.append(f"Linear mixed model fit by {results['method']['method']} {results['method']['details']}")

    if results["formula"]:
        formatted.append(f"Formula: {results['formula']}")

    if results["criterion"]:
        formatted.append(f"{results['criterion']['method']} criterion at convergence: {results['criterion']['criterion']}")

    if results["summary"] is not None:
        formatted.append("Summary of Scaled Residuals")
        formatted.append(results["summary"].__str__())

    if results["fixed_effects"] is not None:
        formatted.append("Fixed Effects")
        formatted.append(results["fixed_effects"].__str__())

    if results["random_effects"] is not None:
        formatted.append("Random Effects")
        formatted.append(results["random_effects"].__str__())
    
    if results["number_of_obs"]:
        formatted.append(f"Number of Observations: {results['number_of_obs']}")

    if results["groups"]:
        formatted.append(f"Groups: {results['groups']['group name']} ({results['groups']['group count']})")

    if results["correlation_fixed_effects"] is not None:
        formatted.append("Correlation of Fixed Effects")
        formatted.append(results["correlation_fixed_effects"].__str__())

    return "\n\n".join(formatted)

# Mengubah hasil menjadi string yang user-friendly
hasil_str = extract_formatted(r_output)
print(hasil_str)

