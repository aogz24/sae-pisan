import re

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

# Fungsi untuk mengganti label statistik
def replace_stat_labels(output):
    # Pola regex untuk mengganti label
    output = re.sub(r'\bMin\b', 'Minimum', output)
    output = re.sub(r'\b1Q\b', 'Quartil 1', output)
    output = re.sub(r'\bMedian\b', 'Median', output)
    output = re.sub(r'\b3Q\b', 'Quartil 3', output)
    output = re.sub(r'\bMax\b', 'Maximum', output)
    output = re.sub(r'\bStd\. Error\b', 'Standard Error', output)
    return output

# Mengubah r_output
r_output_updated = replace_stat_labels(r_output)

# Menampilkan hasil
print(r_output_updated)