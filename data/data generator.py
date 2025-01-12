import pandas as pd
import numpy as np

# Set the number of rows and columns
rows = 100
columns = 10

# Create a dataframe with mixed types for each column
data = {}

for i in range(columns):
    if i % 3 == 0:
        # Integer column
        data[f"col_{i}"] = np.random.randint(0, 100, size=rows)
    elif i % 3 == 1:
        # Float column
        data[f"col_{i}"] = np.random.uniform(0, 100, size=rows)
    else:
        # String column
        data[f"col_{i}"] = [f"string_{j}" for j in range(rows)]

# Create a pandas DataFrame
df = pd.DataFrame(data)

# Save to CSV
df.to_csv('data.csv', index=False)
