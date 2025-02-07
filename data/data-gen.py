import numpy as np
import pandas as pd

# Set seed for reproducibility
np.random.seed(123)

# Define sample size
n = 100  # Ubah sesuai kebutuhan

# Generate random area effect u ~ N(0,1)
u = np.random.normal(0, 1, n)

# Generate auxiliary variables
x1 = np.random.uniform(0, 1, n)  # x1 ~ U(0,1)
x2 = np.random.uniform(1, 5, n)  # x2 ~ U(1,5)

# Set coefficient parameters
beta0 = 0.5  # Ubah sesuai kebutuhan
beta1 = 1.2  # Ubah sesuai kebutuhan
beta2 = -0.8 # Ubah sesuai kebutuhan

# Compute µ
logit_mu = beta0 + beta1 * x1 + beta2 * x2 + u
mu = np.exp(logit_mu) / (1 + np.exp(logit_mu))

# Set π = 1
pi_value = 1

# Compute Beta distribution parameters A and B
A = mu * pi_value
B = (1 - mu) * pi_value

# Generate direct estimate y ~ Beta(A, B)
y = np.random.beta(A, B)

# Calculate variance of y
var_y = (A * B) / ((A + B + 1) * (A + B) ** 2)

# Store results in a dataframe named 'data'
data = pd.DataFrame({'x1': x1, 'x2': x2, 'u': u, 'mu': mu, 'A': A, 'B': B, 'y': y, 'var_y': var_y})

data.to_csv('data/data.csv', index=False)
