'''
defect_heatmap_runner.py

Main script for generating a 2D defect heatmap from CSV data.

This lightweight visualization tool is intended for early debug and defect pattern
triage in wafer processing, tool ramp, or equipment development environments.

Expected input: CSV file with columns: x, y, type, severity

Author: Josh Villanueva
'''

import os
import pandas as pd
import matplotlib.pyplot as plt

# ============================================
# Function: Load defect data from CSV
# ============================================
def load_defect_data(file_path):
    '''
    Load defect CSV into a DataFrame and validate required columns.

    Args:
        file_path (str): Path to defect CSV file.

    Returns:
        pd.DataFrame: DataFrame containing x, y, type, severity columns.

    MATLAB analogy:
        >> T = readtable('example_defects.csv');
    '''
    df = pd.read_csv(file_path)
    required_cols = {'x', 'y', 'type', 'severity'}
    if not required_cols.issubset(df.columns):
        raise ValueError(f'Missing required columns: {required_cols - set(df.columns)}')
    return df

# ============================================
# Function: Plot and save defect heatmap
# ============================================

def plot_defect_map(df, output_path):
    '''
    Generate a 2D scatter plot of defect positions color-coded by type.

    Args:
        df (pd.DataFrame): DataFrame with x, y, type, severity columns.
        output_path (str): File path to save the PNG plot.

    MATLAB analogy:
        >> gscatter(x, y, type);
    '''
    plt.figure(figsize=(8, 6))
    for defect_type in df['type'].unique():
        subset = df[df['type'] == defect_type]
        plt.scatter(
            subset['x'], subset['y'],
            label=defect_type,
            alpha=0.7,
            s=80
        )
    plt.xlabel('X Position')
    plt.ylabel('Y Position')
    plt.title('Spatial Defect Map')
    plt.grid(True, linestyle='--', alpha=0.3)
    plt.legend(title='Defect Type')
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()

# ============================================
# Main Runner
# ============================================

if __name__ == '__main__':
    base_dir = os.path.dirname(__file__)
    input_csv = os.path.join(base_dir, 'example_defects.csv')
    output_png = os.path.join(base_dir, 'defect_heatmap.png')

    df = load_defect_data(input_csv)
    plot_defect_map(df, output_png)

    print(f'Defect heatmap saved to: {output_png}')
