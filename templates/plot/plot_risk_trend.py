'''
plot_risk_trend.py

Generate a time-series scatter plot of risk scores with risk flags highlighted.
Useful for tracking model outputs over time in manufacturing or MSAT settings.

Author: Josh Villanueva
'''

import pandas as pd
import matplotlib.pyplot as plt

# ============================================
# Function: Plot model risk score over time
# ============================================
def plot_risk_trend(df, score_col, flag_col, output_path, threshold_line=None):
    '''
    Plot risk scores over time and save as PNG.

    Parameters:
    - df (pd.DataFrame): DataFrame with 'date' and risk score columns
    - score_col (str): Column name containing model output scores
    - flag_col (str): Column name for boolean risk flags
    - output_path (str): File path to save PNG
    - threshold_line (float): Optional line to show risk threshold

    Returns:
    - None (saves image)
    '''
    df['date'] = pd.to_datetime(df['date'])
    df.sort_values('date', inplace=True)

    colors = df[flag_col].map({True: 'red', False: 'blue'})
    plt.figure(figsize=(10, 6))
    plt.scatter(df['date'], df[score_col], c=colors, alpha=0.8)

    plt.xlabel('Date')
    plt.ylabel('Risk Score')
    plt.title(f'Risk Score Over Time – {score_col}')
    plt.grid(True, linestyle='--', alpha=0.3)
    plt.xticks(rotation=90)

    if threshold_line is not None:
        plt.axhline(y=threshold_line, color='black', linestyle=':', linewidth=1)
        plt.text(df['date'].min(), threshold_line + 0.01,
                 f'Threshold = {threshold_line:.2f}',
                 fontsize=8, color='black', va='bottom')

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
