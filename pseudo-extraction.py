import re

def parse_r_script(r_script):
    # Extract key information from r_script
    out_of_sample_domains = int(re.search(r"Out-of-sample domains:\s+(\d+)", r_script).group(1))
    in_sample_domains = int(re.search(r"In-sample domains:\s+(\d+)", r_script).group(1))
    variance_method = re.search(r"Variance estimation method:\s+([\w\s,]+)", r_script).group(1).strip()
    variance_random_effects = float(re.search(r"Variance of random effects:\s+([\d.]+)", r_script).group(1))
    mse_method = re.search(r"MSE method:\s+([\w\s]+)", r_script).group(1).strip()
    transformation = re.search(r"Transformation:\s+([\w\s]+)", r_script).group(1).strip()

    # Store extracted data in a dictionary
    extracted_data = {
        "Out-of-sample Domains": out_of_sample_domains,
        "In-sample Domains": in_sample_domains,
        "Variance Estimation Method": variance_method,
        "Variance of Random Effects": variance_random_effects,
        "MSE Method": mse_method,
        "Transformation": transformation,
    }

    return extracted_data

def display_extracted_data(data):
    print("Extracted Information:")
    for key, value in data.items():
        print(f"{key}: {value}")

# Example usage
r_script = """Empirical Best Linear Unbiased Prediction (Fay-Herriot)

Out-of-sample domains:  0 
In-sample domains:  12 

Variance and MSE estimation:
Variance estimation method: robustified ml, reblupbc 
k =  1.345 , mult_constant =  1 
Variance of random effects:  397.854 
MSE method:  pseudo linearization 

Transformation: No transformation """

extracted_data = parse_r_script(r_script)
display_extracted_data(extracted_data)