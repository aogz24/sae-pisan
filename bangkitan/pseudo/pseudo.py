import numpy as np
import pandas as pd
import os


num_domains = 10           # D
num_datasets = 10

# Parameter model BHF
beta = np.array([5.0, 2.0])  # Koefisien regresi untuk 2 kovariat
sigma_u2 = 4.0               # Varians efek area
sigma_e2 = 9.0               # Varians error individu

os.makedirs("bangkitan/pseudo", exist_ok=True)

for i in range(num_datasets):
    domain_ids = []
    x1_all = []
    x2_all = []
    u_d_list = []
    e_all = []
    y_all = []
    rse_all = []
    vardir_all = []
    popn_segments_list = []
    meanx1_list = []
    meanx2_list = []

    for d in range(1, num_domains + 1):
        n_d = np.random.randint(4, 16)  # Jumlah unit acak antara 4-15
        u_d = np.random.normal(0, np.sqrt(sigma_u2))  # Efek area domain d

        x1 = np.random.normal(50, 10, n_d)
        x2 = np.random.normal(100, 20, n_d)
        X = np.column_stack((x1, x2))
        e = np.random.normal(0, np.sqrt(sigma_e2), n_d)
        y = X @ beta + u_d + e

        rse = np.random.uniform(5, 25, size=n_d)  # RSE antara 5% - 25%
        vardir = ((y * rse / 100) ** 2)           # vardir dihitung dari Y dan RSE

        domain_ids.extend([d] * n_d)
        x1_all.extend(x1)
        x2_all.extend(x2)
        y_all.extend(y)
        e_all.extend(e)
        u_d_list.extend([u_d] * n_d)
        rse_all.extend(rse)
        vardir_all.extend(vardir)

        # Untuk kolom meanxpop dan popnSegments
        popn_segments = np.random.randint(5, 20)
        popn_segments_list.extend([popn_segments] * n_d)
        meanx1 = np.mean(x1)
        meanx2 = np.mean(x2)
        meanx1_list.extend([meanx1] * n_d)
        meanx2_list.extend([meanx2] * n_d)

    df = pd.DataFrame({
        "Domain": domain_ids,
        "Y": y_all,
        "X1": x1_all,
        "X2": x2_all,
        "u_d": u_d_list,  # ground truth efek area (tidak dipakai dalam model fitting)
        "e": e_all,       # ground truth error (tidak dipakai dalam model fitting)
        "RSE (%)": rse_all,
        "vardir": vardir_all,
        "PopnSegments": popn_segments_list,
        "MeanX1Pop": meanx1_list,
        "MeanX2Pop": meanx2_list
    })
    
    print(f"Dataset {i+1} generated with {num_domains} domains and {len(df)} units.")

    df.to_csv(f"bangkitan/pseudo/dataset_{i+1}.csv", index=False)