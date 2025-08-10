import numpy as np
import pandas as pd
import os


# Parameters
num_datasets = 10
num_rows = 100
beta = np.array([1, -2.5, 0.5, 1.1, -1.3])  # Coefficients for x1 to x5


# Generate datasets
for i in range(num_datasets):
    x1 = np.random.normal(0, 1, num_rows)
    x2 = np.random.normal(0, 1, num_rows)
    x3 = np.random.normal(0, 1, num_rows)
    x4 = np.random.choice(["a", "b"], num_rows)
    x5 = np.random.choice(["sd", "smp", "sma"], num_rows)
    
    x4_encoded = np.where(x4 == "a", 0, 1)  # a=0, b=1
    x5_encoded = np.where(x5 == "sd", 0, np.where(x5 == "smp", 1, 2))  # sd=0, smp=1, sma=2
    
    X = np.vstack((x1, x2, x3, x4_encoded, x5_encoded)).T
    ui = np.random.normal(0, 1, num_rows)
    ei = np.random.normal(0, 1, num_rows)
    
    eta = X @ beta + ui + ei
    
    mu = 1/(1+np.exp(-eta))
    phi = 20
    
    alpha = mu*phi
    beta_param = (1-mu)*phi
    
    y= np.random.beta(alpha, beta_param)
    
    df = pd.DataFrame({
        'x1': x1,
        'x2': x2,
        'x3': x3,
        'x4': x4,  # Original categorical values ("a", "b")
        'x5': x5   # Original categorical values ("sd", "smp", "sma")
    })
    df['y'] = y
    
    rse = np.random.uniform(10,50, size=num_rows)
    vardir = (y*rse/100)**2
    
    df['rse']=rse
    df['vardir'] = vardir
    
    print(i+1)
    file_path = os.path.join("bangkitan","saeHB",f"dataset_{i+1}.csv")
    df.to_csv(file_path, index=False)
