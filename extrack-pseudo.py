def extract_output_results(output):
    """
    Extracts results from the given output string and returns it as a dictionary.
    """
    import re
    results = {}
    
    results['Model'] = 'Pseudo Empirical Best Linear Unbiased Prediction (Fay-Herriot)'

    # Extract out-of-sample and in-sample domains
    results['Out of sample domains'] = int(re.search(r"Out-of-sample domains:\s+(\d+)", output).group(1))
    results['In Sample domains'] = int(re.search(r"In-sample domains:\s+(\d+)", output).group(1))

    # Extract variance estimation method
    results['Variance Estimation Method'] = re.search(r"Variance estimation method:\s+([\w\s,]+)", output).group(1).strip()

    # Extract k and mult_constant
    results['k'] = float(re.search(r"k\s+=\s+([\d.]+)", output).group(1))
    results['Mult constant'] = float(re.search(r"mult_constant\s+=\s+([\d.]+)", output).group(1))

    # Extract variance of random effects
    results['Variance of Random Effect'] = float(re.search(r"Variance of random effects:\s+([\d.]+)", output).group(1))

    # Extract MSE method
    results['MSE Method'] = re.search(r"MSE method:\s+([\w\s]+)", output).group(1).strip()

    # Extract transformation
    results['Transformation'] = re.search(r"Transformation:\s+([\w\s]+)", output).group(1).strip()

    return results

# Example usage
output = """
Empirical Best Linear Unbiased Prediction (Fay-Herriot)

Out-of-sample domains:  0 
In-sample domains:  12 

Variance and MSE estimation:
Variance estimation method: robustified ml, reblupbc 
k =  1.345 , mult_constant =  1 
Variance of random effects:  397.854 
MSE method:  pseudo linearization 

Transformation: No transformation 
"""

extracted_results = extract_output_results(output)
print(extracted_results)