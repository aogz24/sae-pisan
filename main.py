from model.PemodelanSae import PemodelanSae as sae
import pandas as pd
import numpy as np

y = np.random.uniform(size=20)
X = np.random.uniform(size=(20, 10))
dataFrame = pd.DataFrame(X)
dataFrame['target'] = y
saemodel = sae(dataFrame['target'], dataFrame.drop('target', axis=1))
print(saemodel)