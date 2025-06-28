import numpy as np
import pandas as pd
from pathlib import Path


# Parameters
num_datasets = 10      # berapa file CSV
D = 100                # banyaknya domain / baris per file
beta = np.array([1.9, -2.1, 0.85, 1.32, -1.0])   # koefisien untuk x1–x5
A = 0.7                # varian model error v_d  ~ N(0, A)

out_dir = Path("bangkitan") / "saeHB" / "Normal"
out_dir.mkdir(parents=True, exist_ok=True)

for i in range(num_datasets):
    # ----- 1. Auxiliary variables ------------------------------------------------
    x1 = np.random.normal(0, 1, D)
    x2 = np.random.normal(0, 1, D)
    x3 = np.random.normal(0, 1, D)
    x4 = np.random.choice([0, 1], D)
    x5 = np.random.choice([0, 1, 2], D)
    X = np.vstack((x1, x2, x3, x4, x5)).T      # (D × 5)

    # ----- 2. Generate true domain means delta_d ---------------------------------
    v_d = np.random.normal(0, np.sqrt(A), D)    # model error
    delta = X @ beta + v_d

    # ----- 3. Choose (known) sampling variances psi_d = vardir -------------------
    #  → misalnya acak antara 0.2–1.0 (silakan sesuaikan)
    vardir = np.random.uniform(0.1, 1.0, D)

    # ----- 4. Generate direct estimates y = delta + e_d --------------------------
    e_d = np.random.normal(0, np.sqrt(vardir))  # sampling error with correct var
    y = delta + e_d

    # ----- 5. (Opsional) Buat RSE hanya unt uk ilustrasi -------------------------
    rse = 100 * np.sqrt(vardir) / np.maximum(np.abs(delta), 1e-6)  # %
    
    # ----- 6. Simpan ke CSV -------------------------------------------------------
    df = pd.DataFrame({
        'x1': x1, 'x2': x2, 'x3': x3, 'x4': x4, 'x5': x5,
        'y': y,
        'vardir': vardir,
        'rse': rse
    })

    df.to_csv(out_dir / f"dataset_{i+1}.csv", index=False)
    print(f"dataset_{i+1}.csv saved ({D} rows)")