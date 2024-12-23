import numpy as np

# Generate a 1000x1000 array of random numbers
data = np.random.rand(1000, 1000)

# Save the data to a CSV file
np.savetxt("data.csv", data, delimiter=",")