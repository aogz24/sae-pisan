import pandas as pd

# Read the CSV file
df = pd.read_csv("bangkitan/pseudo/populations/eusilcA_pop_1.csv")

# Print the column names
print("Columns in the CSV file:")
print(df.columns.tolist())

# Print the first few rows
print("\nFirst 5 rows:")
print(df.head())

# Check if weight column exists
if 'weight' in df.columns:
    print("\nWeight column exists with values:", df['weight'].head().tolist())
else:
    print("\nWeight column does not exist in the CSV file")
