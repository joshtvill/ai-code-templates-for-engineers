import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# ============================================
# Load Data Function
# ============================================
def load_data(file_path, value_column):
    '''
    Load the process data from a CSV or Excel file.

    Parameters:
    - file_path (str): Path to the input CSV or Excel file
    - value_column (str): Name of the column with numeric values

    Returns:
    - pd.Series: The column of interest as a pandas Series
    '''
    if file_path.endswith('.csv'):
        df = pd.read_csv(file_path)
    elif file_path.endswith(('.xls', '.xlsx')):
        df = pd.read_excel(file_path)
    else:
        raise ValueError("Unsupported file format. Use CSV or Excel.")

    if value_column not in df.columns:
        raise ValueError(f"Column '{value_column}' not found in file.")

    return df[value_column]

# ============================================
# Compute SPC Metrics
# ============================================
def compute_spc_metrics(data):
    '''
    Calculate SPC summary statistics and control limits.

    Parameters:
    - data (pd.Series): Numeric data for SPC analysis

    Returns:
    - dict: Summary statistics
    '''
    mean = data.mean()
    std = data.std()
    ucl = mean + 3 * std  # Upper Control Limit
    lcl = mean - 3 * std  # Lower Control Limit

    # MATLAB Equivalent: mean = mean(x); std = std(x);
    # ucl = mean + 3 * std; lcl = mean - 3 * std;

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
# Detect Outliers
# ============================================
def detect_outliers(data, method='zscore', threshold=3.0):
    '''
    Flag values that are statistical outliers using Z-score or IQR.

    Parameters:
    - data (pd.Series): Numeric data
    - method (str): 'zscore' or 'iqr'
    - threshold (float): Threshold for identifying outliers

    Returns:
    - pd.Series (bool): True where data is an outlier
    '''
    if method == 'zscore':
        z_scores = (data - data.mean()) / data.std()
        return abs(z_scores) > threshold

    elif method == 'iqr':
        Q1 = data.quantile(0.25)
        Q3 = data.quantile(0.75)
        IQR = Q3 - Q1
        return (data < Q1 - threshold * IQR) | (data > Q3 + threshold * IQR)

    else:
        raise ValueError("Invalid method. Choose 'zscore' or 'iqr'.")

# ============================================
# Plot Control Chart
# ============================================
def plot_control_chart(data, stats, outliers=None, output_path='output_chart.png'):
    '''
    Create and save a control chart using matplotlib.

    Parameters:
    - data (pd.Series): Numeric data
    - stats (dict): SPC metrics dictionary
    - outliers (pd.Series): Boolean Series of outliers
    - output_path (str): Path to save the output chart
    '''
    plt.figure(figsize=(12, 6))
    plt.plot(data.index, data.values, marker='o', label='Data')

    # Plot control limits and mean
    plt.axhline(stats['mean'], color='green', linestyle='--', label='Mean')
    plt.axhline(stats['UCL'], color='red', linestyle='--', label='UCL (+3σ)')
    plt.axhline(stats['LCL'], color='red', linestyle='--', label='LCL (-3σ)')

    # Highlight outliers
    if outliers is not None:
        plt.scatter(data.index[outliers], data[outliers], color='red', zorder=5, label='Outliers')

    plt.title('SPC Control Chart')
    plt.xlabel('Sample Index')
    plt.ylabel('Measured Value')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

# ============================================
# Save Flagged Data
# ============================================
def save_flagged_data(data, outliers, output_path='flagged_data.csv'):
    '''
    Export original data with an added outlier flag column.

    Parameters:
    - data (pd.Series): Original numeric data
    - outliers (pd.Series): Boolean mask for outliers
    - output_path (str): Path to save output CSV
    '''
    df = pd.DataFrame({
        'Value': data,
        'Outlier': outliers
    })
    df.to_csv(output_path, index=False)

# ============================================
# Main Runner
# ============================================
def main():
    '''
    Main execution block: load data, compute stats, detect outliers, plot chart, save flagged data.

    Edit file_path and value_column as needed.
    '''
    # Update with your actual file path. If using Windows filepath, use raw string (r'path\to\file.csv')
    # Example: file_path = r'C:\path\to\your\data.csv'
    file_path = 'example_data.csv'
    value_column = 'Thickness_nm'

    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Define output paths relative to the script directory
    chart_path = os.path.join(script_dir, 'output_chart.png')
    csv_path = os.path.join(script_dir, 'flagged_data.csv')

    # Run SPC pipeline
    data = load_data(file_path, value_column)
    stats = compute_spc_metrics(data)
    outliers = detect_outliers(data, method='zscore', threshold=3.0)

    plot_control_chart(data, stats, outliers, output_path=chart_path)
    save_flagged_data(data, outliers, output_path=csv_path)

    # Print results to console
    print("Summary Statistics:")
    for k, v in stats.items():
        print(f"  {k}: {v:.2f}")
    print(f"Total Outliers Detected: {outliers.sum()}")

# Only run main() when executed directly, not imported
if __name__ == '__main__':
    main()