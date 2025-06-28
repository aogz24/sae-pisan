import numpy as np
import pandas as pd
import os

m = 100

for i in range(10):
    x1 = np.random.uniform(0, 1, m)
    x2 = np.random.uniform(0, 1, m)
    x3 = np.random.uniform(0, 1, m)
    x4 = np.random.uniform(0, 1, m)

    # b0 = b1 = b2 = b3 = b4 = 0.5
    u = np.random.normal(0, 1, m)
    pi = np.random.gamma(shape=1, scale=1/0.5)  # scale = 1/rate

    lin_pred = 0.1 + 0.62*x1 + 0.2*x2 + 0.3*x3 + 0.7*x4 + u
    Mu = np.exp(lin_pred) / (1 + np.exp(lin_pred))

    A = Mu * pi
    B = (1 - Mu) * pi

    y = np.random.beta(A, B)
    y = np.where(y >= 1.0, 0.99999999, y)
    y = np.where(y <= 0.0, 0.00000001, y)

    MU = A / (A + B)
    vardir = A * B / (((A + B)**2) * (A + B + 1))

    dataBeta = pd.DataFrame({
        'y': y,
        'x1': x1,
        'x2': x2,
        'x3': x3,
        'x4': x4,
        'vardir': vardir
    })
    
    print(i+1)
    file_path = os.path.join("bangkitan","saeHB", "Beta",f"dataset_{i+1}.csv")
    dataBeta.to_csv(file_path, index=False)