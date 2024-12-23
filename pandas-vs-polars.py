import pandas as pd
import polars as pl
import time

# File path
csv_file = 'data/data_20241223_1000000.csv'

# Load CSV with pandas
start_time = time.time()
df_pandas = pd.read_csv(csv_file)
pandas_duration = time.time() - start_time
print(f"Pandas load time: {pandas_duration:.4f} seconds")

# Load CSV with polars
start_time = time.time()
df_polars = pl.read_csv(csv_file)
polars_duration = time.time() - start_time
print(f"Polars load time: {polars_duration:.4f} seconds")

# Perform a simple operation with pandas
start_time = time.time()
pandas_sum = df_pandas['col_2'].sum()
pandas_operation_duration = time.time() - start_time
print(f"Pandas sum operation time: {pandas_operation_duration:.4f} seconds")

# Perform a simple operation with polars
start_time = time.time()
polars_sum = df_polars['col_2'].sum()
polars_operation_duration = time.time() - start_time
print(f"Polars sum operation time: {polars_operation_duration:.4f} seconds")



# Print comparison items separately
comparison_data = {
    "Metric": ["Load Time", "Sum Operation Time"],
    "Pandas (seconds)": [pandas_duration, pandas_operation_duration],
    "Polars (seconds)": [polars_duration, polars_operation_duration]
}

comparison_df = pd.DataFrame(comparison_data)
print("\nComparison DataFrame:")
print(comparison_df)

# Save comparison to CSV
comparison_csv_file = 'data/comparison_results.csv'
comparison_df.to_csv(comparison_csv_file, index=False)
print(f"\nComparison results saved to {comparison_csv_file}")
