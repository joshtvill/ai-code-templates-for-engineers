'''
save_dataframe_to_csv.py

Utility function to export a DataFrame to CSV with clean overwrite logic.

Intended for use in batch scoring, SPC output, or defect mapping pipelines.
Warns on overwrite and preserves index toggle flexibility.

Author: Josh Villanueva
'''

import pandas as pd
import os

# ============================================
# Function: Save DataFrame to CSV file
# ============================================
def save_dataframe_to_csv(df, output_path, include_index=False, overwrite=True):
    '''
    Save a pandas DataFrame to a CSV file.

    Parameters:
    - df (pd.DataFrame): The DataFrame to export
    - output_path (str): Full path to output CSV
    - include_index (bool): Whether to include the DataFrame index in output
    - overwrite (bool): Whether to overwrite existing files

    Returns:
    - None (writes file to disk)
    '''
    if not overwrite and os.path.exists(output_path):
        print(f"File already exists and overwrite=False: {output_path}")
        return

    try:
        df.to_csv(output_path, index=include_index)
        print(f"Saved DataFrame to: {output_path}")
    except Exception as e:
        print(f"Failed to save DataFrame: {e}")

# ============================================
# Optional Test Block
# ============================================
if __name__ == '__main__':
    # Sample test DataFrame
    sample_df = pd.DataFrame({
        'A': [1, 2, 3],
        'B': ['x', 'y', 'z']
    })
    save_path = 'test_output.csv'
    save_dataframe_to_csv(sample_df, save_path, include_index=False)
