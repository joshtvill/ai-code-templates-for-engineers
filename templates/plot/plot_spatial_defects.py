'''
plot_spatial_defects.py

Create a 2D scatter plot of defect locations color-coded by defect type.
Useful for wafer mapping, spatial clustering, and early triage.

Author: Josh Villanueva
'''

import matplotlib.pyplot as plt

# ============================================
# Function: Plot spatial defect distribution
# ============================================
def plot_spatial_defects(df, output_path):
    '''
    Plot (x, y) locations of defects with color grouping by type.

    Parameters:
    - df (pd.DataFrame): Must contain 'x', 'y', and 'type' columns
    - output_path (str): File path to save PNG

    Returns:
    - None (saves image)
    '''
    plt.figure(figsize=(8, 6))
    for defect_type in df['type'].unique():
        subset = df[df['type'] == defect_type]
        plt.scatter(
            subset['x'], subset['y'],
            label=defect_type,
            alpha=0.7, s=80
        )

    plt.xlabel('X Position')
    plt.ylabel('Y Position')
    plt.title('Spatial Defect Map')
    plt.grid(True, linestyle='--', alpha=0.3)
    plt.legend(title='Defect Type')
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
