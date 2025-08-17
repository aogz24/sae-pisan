import numpy as np
import pandas as pd
import os

# Parameters
population_size = 1000  # Total population size
sample_size = 100      # Sample size (in this case same as population since we want 100%)
num_districts = 5      # Number of districts
num_states = 3         # Number of states
num_datasets = 10     # Number of different datasets to generate

# Create districts and states
states = ["State" + str(i+1) for i in range(num_states)]
districts = ["District" + str(i+1) for i in range(num_districts)]

# Function to generate data similar to eusilcA
def generate_eusilcA_data():
    # Initialize lists for each column
    data = {
        "eqIncome": [],
        "gender": [],
        "eqsize": [],
        "cash": [],
        "self_empl": [],
        "unempl_ben": [],
        "age_ben": [],
        "surv_ben": [],
        "sick_ben": [],
        "dis_ben": [],
        "rent": [],
        "fam_allow": [],
        "house_allow": [],
        "cap_inv": [],
        "tax_adj": [],
        "state": [],
        "district": [],
        "weight": []
    }
    
    # Generate data for each individual
    for _ in range(population_size):
        # Randomly assign state and district
        state = np.random.choice(states)
        district = np.random.choice(districts)
        
        # Generate equivalent income (similar distribution to eusilcA)
        eq_income = np.random.normal(20000, 5000)
        
        # Generate gender
        gender = np.random.choice(["male", "female"])
        
        # Generate equivalent household size
        eq_size = np.random.uniform(1, 3)
        
        # Generate income components with some dependencies
        cash = np.random.normal(15000, 10000) if np.random.random() > 0.3 else 0
        self_empl = np.random.normal(10000, 8000) if np.random.random() > 0.7 else 0
        
        # Generate benefits
        unempl_ben = np.random.normal(5000, 2000) if np.random.random() > 0.8 else 0
        age_ben = np.random.normal(10000, 3000) if np.random.random() > 0.7 else 0
        surv_ben = np.random.normal(8000, 2000) if np.random.random() > 0.9 else 0
        sick_ben = np.random.normal(3000, 1000) if np.random.random() > 0.9 else 0
        dis_ben = np.random.normal(7000, 2000) if np.random.random() > 0.9 else 0
        
        # Generate other financial components
        rent = np.random.normal(4000, 2000) if np.random.random() > 0.8 else 0
        fam_allow = np.random.normal(2000, 1000) if np.random.random() > 0.7 else 0
        house_allow = np.random.normal(3000, 1500) if np.random.random() > 0.8 else 0
        cap_inv = np.random.exponential(1000) if np.random.random() > 0.6 else 0
        tax_adj = -np.random.normal(1000, 500) if np.random.random() > 0.5 else 0
        
        # Generate weight (sampling weight)
        weight = population_size / sample_size  # In this case it's 1 since we're sampling 100%
        
        # Add data to the dictionary
        data["eqIncome"].append(eq_income)
        data["gender"].append(gender)
        data["eqsize"].append(eq_size)
        data["cash"].append(cash)
        data["self_empl"].append(self_empl)
        data["unempl_ben"].append(unempl_ben)
        data["age_ben"].append(age_ben)
        data["surv_ben"].append(surv_ben)
        data["sick_ben"].append(sick_ben)
        data["dis_ben"].append(dis_ben)
        data["rent"].append(rent)
        data["fam_allow"].append(fam_allow)
        data["house_allow"].append(house_allow)
        data["cap_inv"].append(cap_inv)
        data["tax_adj"].append(tax_adj)
        data["state"].append(state)
        data["district"].append(district)
        data["weight"].append(weight)
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Round numerical values to 2 decimal places (except eqsize which needs more precision)
    for col in df.columns:
        if col != "gender" and col != "state" and col != "district" and col != "eqsize":
            df[col] = df[col].round(2)
    
    return df

# Generate population data
population_df = generate_eusilcA_data()

# Create directories if they don't exist
os.makedirs("bangkitan/pseudo/populations", exist_ok=True)
os.makedirs("bangkitan/pseudo/samples", exist_ok=True)

# Generate multiple datasets
for dataset_num in range(1, num_datasets + 1):
    # Set a different random seed for each dataset
    np.random.seed(42 + dataset_num)
    
    # Generate population data
    population_df = generate_eusilcA_data()
    
    # Save population data
    population_df.to_csv(f"bangkitan/pseudo/populations/eusilcA_pop_{dataset_num}.csv", index=False)
    
    # Since sample size is the same as population size, sample data is the same as population data
    sample_df = population_df.copy()
    sample_df.to_csv(f"bangkitan/pseudo/samples/eusilcA_smp_{dataset_num}.csv", index=False)
    
    if dataset_num % 20 == 0:
        print(f"Generated {dataset_num} datasets...")

print(f"Data generation complete! Created {num_datasets} population and sample datasets.")
