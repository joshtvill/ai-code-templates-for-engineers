'''
detect_outliers_iqr.py

Detect outliers using the Interquartile Range (IQR) method.

This non-parametric approach flags values outside the typical spread 
of the data and is more robust to skewed distributions.

Author: Josh Villanueva
'''

import pandas as pd

# ============================================
# Function: Detect outliers using IQR
# ============================================
def detect_outliers_iqr(data, threshold=1.5):
    '''
    Identify outliers using the IQR rule.

    Parameters:
    - data (pd.Series): Numeric values
    - threshold (float): Multiplier for IQR to set boundary

    Returns:
    - pd.Series (bool): True where value is an outlier
    '''
    Q1 = data.quantile(0.25)
    Q3 = data.quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - threshold * IQR
    upper_bound = Q3 + threshold * IQR
    return (data < lower_bound) | (data > upper_bound)

# ============================================
# Optional Test Block
# ============================================
if __name__ == '__main__':
    sample_data = pd.Series([1.0, 1.1, 1.2, 10.0, 1.1, 1.2])
    flags = detect_outliers_iqr(sample_data, threshold=1.5)
    print("IQR Outliers:")
    print(flags)
