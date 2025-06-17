'''
plot_control_chart.py

Generate and save a simple control chart with mean and ±3σ control limits.
Outliers can be highlighted based on a boolean Series.

Author: Josh Villanueva
'''

import matplotlib.pyplot as plt
import pandas as pd

# ============================================
# Function: Plot a control chart
# ============================================
def plot_control_chart(data, stats, outliers=None, output_path='control_chart.png'):
    '''
    Create a control chart and save it as PNG.

    Parameters:
    - data (pd.Series): Numeric data
    - stats (dict): Must include 'mean', 'UCL', 'LCL'
    - outliers (pd.Series): Boolean mask of same length as data (optional)
    - output_path (str): File path for saving the image

    Returns:
    - None (chart saved to file)
    '''
    plt.figure(figsize=(10, 5))
    plt.plot(data.index, data.values, marker='o', label='Data')

    plt.axhline(stats['mean'], color='green', linestyle='--', label='Mean')
    plt.axhline(stats['UCL'], color='red', linestyle='--', label='UCL (+3σ)')
    plt.axhline(stats['LCL'], color='red', linestyle='--', label='LCL (-3σ)')

    if outliers is not None:
        plt.scatter(data.index[outliers], data[outliers], color='red', zorder=5, label='Outliers')

    plt.title('Control Chart')
    plt.xlabel('Index')
    plt.ylabel('Value')
    plt.grid(True, linestyle='--', alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
