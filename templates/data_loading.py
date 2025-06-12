# Template functions for loading CSV data

import pandas as pd

def load_csv(filepath):
    """
    Load a CSV file into a pandas DataFrame.
    Args:
        filepath (str): Path to the CSV file
    Returns:
        pd.DataFrame: Loaded DataFrame
    """
    try:
        df = pd.read_csv(filepath)
        print(f"Loaded {len(df)} rows from {filepath}")
        return df
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return None
