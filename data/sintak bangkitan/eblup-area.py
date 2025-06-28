import numpy as np
import pandas as pd
import os


# Parameters
num_datasets = 10
num_rows = 100
beta = np.array([1.5, -2.0, 0.5, 1.0, -1.0])  # Coefficients for x1 to x5


# Generate datasets
for i in range(num_datasets):
    x1 = np.random.normal(0, 1, num_rows)
    x2 = np.random.normal(0, 1, num_rows)
    x3 = np.random.normal(0, 1, num_rows)
    x4 = np.random.choice([0, 1], num_rows)
    x5 = np.random.choice([0, 1, 2], num_rows)
    
    X = np.vstack((x1, x2, x3, x4, x5)).T
    ui = np.random.normal(0, 1, num_rows)
    ei = np.random.normal(0, 1, num_rows)
    
    y = X @ beta + ui + ei
    
    df = pd.DataFrame(X, columns=['x1', 'x2', 'x3', 'x4', 'x5'])
    df['y'] = y
    
    rse = np.random.uniform(10,50, size=num_rows)
    vardir = (y*rse/100)**2
    
    df['rse']=rse
    df['vardir'] = vardir
    
    print(i)
    file_path = os.path.join("bangkitan","eblup_area",f"dataset_{i+1}.csv")
    df.to_csv(file_path, index=False)
