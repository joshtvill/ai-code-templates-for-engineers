'''
detect_outliers_zscore.py

Flag statistical outliers using Z-score method based on standard deviation.

This is commonly used in SPC or lab environments for identifying values 
that deviate significantly from a population mean.

Author: Josh Villanueva
'''

import pandas as pd

# ============================================
# Function: Detect outliers using Z-score
# ============================================
def detect_outliers_zscore(data, threshold=3.0):
    '''
    Identify outliers based on standard deviation threshold.

    Parameters:
    - data (pd.Series): Numeric values
    - threshold (float): Number of standard deviations to define outlier

    Returns:
    - pd.Series (bool): True where value is an outlier
    '''
    z_scores = (data - data.mean()) / data.std()
    return abs(z_scores) > threshold

# ============================================
# Optional Test Block
# ============================================
if __name__ == '__main__':
    sample_data = pd.Series([1.0, 1.1, 1.2, 10.0, 1.1, 1.2])
    flags = detect_outliers_zscore(sample_data, threshold=2.5)
    print("Z-score Outliers:")
    print(flags)
