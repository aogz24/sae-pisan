import numpy as np
import pandas as pd

def neet_logistic(WEIGHT, STRATA, PROV, REGENCY, income, sex, age, disability, edu, domain, random_state=None):
    np.random.seed(random_state)
    beta_0 = -2.0
    beta_weight = 0.2
    beta_income = -0.0000001
    beta_sex = 0.5
    beta_age = 0.03
    beta_disability = 1.0
    beta_edu = -0.3
    beta_domain = 0.05

    # Linear combination
    z = (beta_0
         + beta_weight * WEIGHT
         + beta_income * income
         + beta_sex * sex
         + beta_age * age
         + beta_disability * disability
         + beta_edu * edu
         + beta_domain * domain)

    # Tambahkan error acak (noise)
    error = np.random.normal(0, 0.5, len(WEIGHT))
    z += error

    # Fungsi logistik
    prob = 1 / (1 + np.exp(-z))

    # Hasil biner NEET (0/1)
    neet = np.random.binomial(1, prob)
    return neet, prob

n_samples = 100
prov_codes = [11, 12, 13, 14, 15, 16, 17, 18, 19, 21, 31, 32, 33, 34, 35, 36, 51, 52, 53, 61, 62, 63, 64, 65, 71, 72, 73, 74, 75, 76, 81, 82, 91, 92]
ID = np.arange(1, n_samples + 1)
WEIGHT = np.round(np.random.normal(1.0, 0.3, n_samples), 3)
STRATA = np.random.randint(1, 2, n_samples)
PROV = np.random.choice(prov_codes, n_samples)
REGENCY = [int(f"{prov}{np.random.randint(1, 100):02d}") for prov in PROV]
income = np.round(np.random.normal(7500000, np.sqrt(2500000), n_samples), 2)
sex = np.random.randint(0, 2, n_samples)
age = np.random.randint(15, 66, n_samples)
disability = np.random.randint(0, 2, n_samples)
edu = np.random.randint(1, 7, n_samples)
domain = np.random.randint(1, 11, n_samples)

neet, prob = neet_logistic(WEIGHT, STRATA, PROV, REGENCY, income, sex, age, disability, edu, domain)

df = pd.DataFrame({
    'ID': ID,
    'WEIGHT': WEIGHT,
    'STRATA': STRATA,
    'PROV': PROV,
    'REGENCY': REGENCY,
    'income': income,
    'sex': sex,
    'age': age,
    'disability': disability,
    'edu': edu,
    'domain': domain,
    'neet': neet
})

print(df.head())
# print(f"Summary Statistics:\n{df.describe()}")