'''
compute_spc_metrics.py

Calculate basic statistical process control (SPC) metrics for a numeric dataset.

This includes mean, standard deviation, and ±3σ control limits.
Useful for early trend monitoring, deviation detection, or baseline stability.

Author: Josh Villanueva
'''

import pandas as pd

# ============================================
# Function: Compute SPC summary statistics
# ============================================
def compute_spc_metrics(data):
    '''
    Compute mean, standard deviation, and control limits.

    Parameters:
    - data (pd.Series): Numeric values (e.g., yield, thickness)

    Returns:
    - dict: Summary statistics (mean, std, UCL, LCL, min, max)
    '''
    mean = data.mean()
    std = data.std()
    ucl = mean + 3 * std
    lcl = mean - 3 * std

    stats = {
        'mean': mean,
        'std': std,
        'min': data.min(),
        'max': data.max(),
        'UCL': ucl,
        'LCL': lcl
    }
    return stats

# ============================================
# Optional Test Block
# ============================================
if __name__ == '__main__':
    # Example input data
    sample_data = pd.Series([1.1, 1.2, 1.0, 1.3, 1.1, 1.4])
    stats = compute_spc_metrics(sample_data)
    print("SPC Metrics:")
    for k, v in stats.items():
        print(f"  {k}: {v:.3f}")
