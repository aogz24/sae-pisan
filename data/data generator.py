import pandas as pd
import numpy as np

# Set the number of rows
rows = 1000000

# Create a dataframe with the specified columns
data = {
    "y": np.random.uniform(0, 1, size=rows),
    "x1": np.random.choice(["aku", "kamu", "dia", "kita", "mereka"], size=rows),
    "x6": np.random.uniform(0, 100, size=rows),
    "x7": np.random.uniform(0, 100, size=rows),
    "x8": np.random.uniform(0, 100, size=rows),
    "x9": np.random.uniform(0, 100, size=rows),
    "x10": np.random.uniform(0, 100, size=rows),
    "x11": np.random.uniform(0, 100, size=rows),
    "vardir": np.random.uniform(0, 100, size=rows),
    "major_area": np.random.randint(0, 3, size=rows)
}

# Create a pandas DataFrame
df = pd.DataFrame(data)

# Save to CSV
df.to_csv('data-coba-coba.csv', index=False)
