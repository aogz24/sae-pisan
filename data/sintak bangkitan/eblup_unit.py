import numpy as np
import pandas as pd
import os

np.random.seed(42)

num_counties = 10
total_rows = 100
num_datasets = 10

os.makedirs("bangkitan/eblup_unit", exist_ok=True)

for i in range(num_datasets):
    county = np.tile(np.arange(1, num_counties + 1), total_rows // num_counties)
    if len(county) < total_rows:
        county = np.concatenate([county, np.random.choice(np.arange(1, num_counties + 1), total_rows - len(county))])
    county = county[:total_rows]

    corn_hec = np.random.normal(100, 20, total_rows)
    soybeans_hec = np.random.normal(80, 15, total_rows)
    corn_pix = np.random.normal(200, 30, total_rows)
    soybeans_pix = np.random.normal(150, 25, total_rows)
    rse = np.random.uniform(10,50, size=total_rows)
    vardir_corn_hec = (corn_hec*rse/100)**2
    vardir_soybean = (soybeans_hec*rse/100)**2
    
    

    mean_corn_pix_per_seg = np.random.normal(200, 10, num_counties)
    mean_soybeans_pix_per_seg = np.random.normal(150, 8, num_counties)
    popn_segments = np.random.randint(5, 20, num_counties)
    
    # Inisialisasi kolom dengan NaN
    mean_corn_pix_per_seg_col = [mean_corn_pix_per_seg[i] if i < 10 else np.nan for i in range(total_rows)]
    mean_soybeans_pix_per_seg_col = [mean_soybeans_pix_per_seg[i] if i < 10 else np.nan for i in range(total_rows)]
    county_index_duplicated_0_col = [county[i] if i < 10 else np.nan for i in range(total_rows)]
    popn_segments_col = [popn_segments[i] if i < 10 else np.nan for i in range(total_rows)]

    county_index = county
    county_index_duplicated_0 = county

    df = pd.DataFrame({
        "County": county,
        "CornHec": corn_hec,
        "SoyBeansHec": soybeans_hec,
        "CornPix": corn_pix,
        "SoyBeansPix": soybeans_pix,
        "CountyIndex": county,
        "MeanCornPixPerSeg": mean_corn_pix_per_seg_col,
        "MeanSoyBeansPixPerSeg": mean_soybeans_pix_per_seg_col,
        "CountyIndex_duplicated_0": county_index_duplicated_0_col,
        "PopnSegments": popn_segments_col,
        "RSE (%)": rse,
        "vardir corn": vardir_corn_hec,
        "vardir soy": vardir_soybean
    })

    df.to_csv(f"bangkitan/eblup_unit/unit_level_{i+1}.csv", index=False)