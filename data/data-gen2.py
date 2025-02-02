import pandas as pd

# Data untuk CornSoybean
data_cornsoybean = {
    "County": [1, 2, 3, 4, 4, 5, 5, 5, 6, 6, 6, 7, 7, 7, 8, 8, 8, 9, 9, 9, 9, 10, 10, 10, 10, 10, 11, 11, 11, 11, 11, 12, 12, 12, 12, 12, 12],
    "CornHec": [165.76, 96.32, 76.08, 185.35, 116.43, 162.08, 152.04, 161.75, 92.88, 149.94, 64.75, 127.07, 133.55, 77.70, 206.39, 108.33, 118.17, 99.96, 140.43, 98.95, 131.04, 114.12, 100.60, 127.88, 116.90, 87.41, 93.48, 121.00, 109.91, 122.66, 104.21, 88.59, 88.59, 165.35, 104.00, 88.63, 153.70],
    "SoyBeansHec": [8.09, 106.03, 103.60, 6.47, 63.82, 43.50, 71.43, 42.49, 105.26, 76.49, 174.34, 95.67, 76.57, 93.48, 37.84, 131.12, 124.44, 144.15, 103.60, 88.59, 115.58, 99.15, 124.56, 110.88, 109.14, 143.66, 91.05, 132.33, 143.14, 104.13, 118.57, 102.59, 29.46, 69.28, 99.15, 143.66, 94.49],
    "CornPix": [374, 209, 253, 432, 367, 361, 288, 369, 206, 316, 145, 355, 295, 223, 459, 290, 307, 252, 293, 206, 302, 313, 246, 353, 271, 237, 221, 369, 343, 342, 294, 220, 340, 355, 261, 187, 350],
    "SoyBeansPix": [55, 218, 250, 96, 178, 137, 206, 165, 218, 221, 338, 128, 147, 204, 77, 217, 258, 303, 221, 222, 274, 190, 270, 172, 228, 297, 167, 191, 249, 182, 179, 262, 87, 160, 221, 345, 190]
}
df_cornsoybean = pd.DataFrame(data_cornsoybean)

# Data untuk Xmean
data_xmean = {
    "CountyIndex": list(range(2, 14)),
    "MeanCornPixPerSeg": [295.29, 300.40, 289.60, 290.74, 318.21, 257.17, 291.77, 301.26, 262.17, 314.28, 298.65, 325.99],
    "MeanSoyBeansPixPerSeg": [189.70, 196.65, 205.28, 220.22, 188.06, 247.13, 185.37, 221.36, 247.09, 198.66, 204.61, 177.05]
}
df_xmean = pd.DataFrame(data_xmean)

# Data untuk Popn
data_popn = {
    "CountyIndex": list(range(2, 14)),
    "PopnSegments": [545, 566, 394, 424, 564, 570, 402, 567, 687, 569, 965, 556]
}
df_popn = pd.DataFrame(data_popn)

# Menggabungkan semua DataFrame menjadi satu CSV
df_combined = pd.concat([df_cornsoybean, df_xmean, df_popn], axis=1)
df_combined.to_csv("combined_data.csv", index=False)

# Menampilkan hasil
print("CornSoybean DataFrame:")
print(df_cornsoybean)
print("\nXmean DataFrame:")
print(df_xmean)
print("\nPopn DataFrame:")
print(df_popn)
