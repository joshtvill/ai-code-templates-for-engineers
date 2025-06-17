'''
load_csv_file.py

Reusable function to load CSV data into a pandas DataFrame with error handling.

This I/O utility is designed to be dropped into any data processing script.
Includes basic printout and fallback to empty DataFrame on failure.

Typical use cases:
- Batch logs
- Measurement outputs
- Experimental metadata tables

Author: Josh Villanueva
'''

import pandas as pd

# ============================================
# Function: Load CSV file with error handling
# ============================================
def load_csv_file(file_path, file_type='generic'):
    '''
    Load a CSV file into a DataFrame.

    Parameters:
    - file_path (str): Full path to the input CSV file
    - file_type (str): Optional label for console logging

    Returns:
    - pd.DataFrame: Loaded DataFrame or empty fallback on failure
    '''
    try:
        df = pd.read_csv(file_path)
        print(f"Loaded {file_type}: {df.shape[0]} rows")
        return df
    except Exception as e:
        print(f"Failed to load {file_type} file: {e}")
        return pd.DataFrame()

# ============================================
# Optional Test Block
# ============================================
if __name__ == '__main__':
    # Example usage (update path as needed)
    test_path = 'example_data.csv'
    df = load_csv_file(test_path, file_type='Example')
