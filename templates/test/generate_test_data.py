'''
generate_test_data.py

Utility to generate synthetic data for testing pipeline functions or plotting behavior.
Simulates features, timestamps, quality outcomes, and defect types.

Intended for use when validating templates or mocking a real-world scenario.

Author: Josh Villanueva
'''

import pandas as pd
import numpy as np
import random

# ============================================
# Function: Generate test batch data
# ============================================
def generate_batch_data(n=50, seed=42):
    '''
    Create synthetic batch process data and QC outcomes.

    Parameters:
    - n (int): Number of batches to simulate
    - seed (int): Random seed for reproducibility

    Returns:
    - pd.DataFrame: DataFrame with process inputs and outcome
    '''
    np.random.seed(seed)
    random.seed(seed)

    dates = pd.date_range(end=pd.Timestamp.today(), periods=n).to_list()
    batch_ids = [f"B{i+1:03d}" for i in range(n)]

    df = pd.DataFrame({
        'batch_id': batch_ids,
        'date': dates,
        'component_A': np.random.normal(1.2, 0.1, size=n),
        'avg_pH': np.random.normal(7.0, 0.15, size=n),
        'final_yield': np.random.normal(0.91, 0.04, size=n)
    })
    return df

# ============================================
# Function: Generate test defect map data
# ============================================
def generate_defect_data(n=200, seed=24):
    '''
    Create synthetic spatial defect map data.

    Parameters:
    - n (int): Number of defects
    - seed (int): Random seed

    Returns:
    - pd.DataFrame: DataFrame with x, y, type, and severity
    '''
    np.random.seed(seed)
    types = ['scratch', 'particle', 'void', 'contamination']
    df = pd.DataFrame({
        'x': np.random.uniform(0, 100, n),
        'y': np.random.uniform(0, 100, n),
        'type': np.random.choice(types, n),
        'severity': np.random.randint(1, 6, n)
    })
    return df

# ============================================
# Optional Test Block
# ============================================
if __name__ == '__main__':
    batch_df = generate_batch_data()
    defect_df = generate_defect_data()

    print("Example batch data:")
    print(batch_df.head())

    print("Example defect data:")
    print(defect_df.head())
