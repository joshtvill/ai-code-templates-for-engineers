'''
append_to_log.py

Append new rows to a cumulative CSV file (e.g., for batch history tracking).

Typical use case: Extend a master log with risk-scored batch records after model application.
If the file does not exist, it will be created. Otherwise, the new rows are appended.

Author: Josh Villanueva
'''

import pandas as pd
import os

# ============================================
# Function: Append new rows to a cumulative CSV log
# ============================================
def append_to_log(df, log_path, features_to_log):
    '''
    Add selected columns from a DataFrame to a persistent CSV log.

    Parameters:
    - df (pd.DataFrame): DataFrame containing new data to log
    - log_path (str): Full file path to the existing or new CSV file
    - features_to_log (list): List of column names to include in the log

    Returns:
    - None (writes combined log to disk)
    '''
    # Subset DataFrame to the desired columns for logging
    new_data = df[features_to_log]

    try:
        # If log file exists, append; otherwise create new log
        if os.path.exists(log_path):
            existing = pd.read_csv(log_path)
            combined = pd.concat([existing, new_data], ignore_index=True)
        else:
            combined = new_data

        # Save updated log
        combined.to_csv(log_path, index=False)
        print(f"Updated master log: {log_path}")

    except Exception as e:
        print(f"Error writing to log: {e}")

# ============================================
# Optional Test Block
# ============================================
if __name__ == '__main__':
    # Example: Append test DataFrame to log file
    sample_df = pd.DataFrame({
        'batch_id': ['B001', 'B002'],
        'date': ['2024-01-01', '2024-01-02'],
        'risk_score': [0.21, 0.87],
        'risk_flag': [False, True]
    })
    output_log_path = 'batch_history_log.csv'
    selected_cols = ['batch_id', 'date', 'risk_score', 'risk_flag']

    append_to_log(sample_df, output_log_path, selected_cols)
