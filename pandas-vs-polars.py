import pandas as pd
import polars as pl
import time
import tracemalloc

# Save the DataFrame to a CSV file
csv_file = 'data-coba-coba.csv'

# Function to measure time and memory
def measure_time_and_memory(func, *args, **kwargs):
    tracemalloc.start()
    start_time = time.time()
    result = func(*args, **kwargs)
    duration = time.time() - start_time
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return result, duration, current, peak

# Load CSV with pandas
df_pandas, pandas_load_time, pandas_load_mem, pandas_load_peak = measure_time_and_memory(pd.read_csv, csv_file)
print(f"Pandas load time: {pandas_load_time:.4f} seconds, Memory: {pandas_load_mem / 1024:.2f} KB, Peak: {pandas_load_peak / 1024:.2f} KB")

# Load CSV with polars
df_polars, polars_load_time, polars_load_mem, polars_load_peak = measure_time_and_memory(pl.read_csv, csv_file)
print(f"Polars load time: {polars_load_time:.4f} seconds, Memory: {polars_load_mem / 1024:.2f} KB, Peak: {polars_load_peak / 1024:.2f} KB")

# Create a DataFrame for the benchmark results
benchmark_results = pd.DataFrame({
    "Library": ["Pandas", "Polars"],
    "Load Time (s)": [pandas_load_time, polars_load_time],
    "Memory (KB)": [pandas_load_mem / 1024, polars_load_mem / 1024],
    "Peak Memory (KB)": [pandas_load_peak / 1024, polars_load_peak / 1024]
})

print("\nBenchmark Results:")
print(benchmark_results)
