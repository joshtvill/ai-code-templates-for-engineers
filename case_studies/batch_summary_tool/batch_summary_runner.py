'''
batch_summary_runner.py

Main script for parsing, merging, and analyzing batch history data from multi-source logs.

This lightweight triage tool is designed for early risk detection and traceability audits
in a biotech or manufacturing process development environment.

Expected inputs: CSV files with batch run logs, QC results, and supplier COA data.

Author: Josh Villanueva
'''

import os
import pandas as pd
import matplotlib.pyplot as plt

# ============================================
# Function: Load generic CSV data
# ============================================
def load_csv_file(file_path, file_type='generic'):
    '''
    Load CSV file into a DataFrame.

    Args:
        file_path (str): Full path to the input CSV file.
        file_type (str): Optional label used for logging.

    Returns:
        pd.DataFrame: Parsed table from file.

    MATLAB analogy:
        >> T = readtable('example_batch_log.csv');
    '''
    try:
        df = pd.read_csv(file_path)
        print(f"Loaded {file_type} data: {df.shape[0]} rows")
        return df
    except Exception as e:
        print(f"Failed to load {file_type} file: {e}")
        return pd.DataFrame()

# ============================================
# Function: Merge batch, QC, and COA data
# ============================================
def merge_batch_data(batch_df, qc_df, coa_df):
    '''
    Merge batch log, QC results, and COA data based on shared keys.

    Args:
        batch_df (pd.DataFrame): Batch-level process data.
        qc_df (pd.DataFrame): Final quality check results.
        coa_df (pd.DataFrame): Supplier component details.

    Returns:
        pd.DataFrame: Combined record per batch_id.

    Note:
        Assumes "batch_id" and "supplier_lot" exist across dataframes.
    '''
    try:
        merged = pd.merge(batch_df, qc_df, on='batch_id', how='left')
        merged = pd.merge(merged, coa_df, on='supplier_lot', how='left')
        print(f"Merged data shape: {merged.shape}")
        return merged
    except Exception as e:
        print(f"Merge error: {e}")
        return pd.DataFrame()

# ============================================
# Function: Apply rule-based risk scoring
# ============================================
def apply_risk_rules(df):
    '''
    Add binary flags and normalized risk score for each batch.

    Rule logic:
        Risk is higher when component_A is high AND avg_pH is low.

    Adds:
        - "risk_flag": True/False for high-risk rule
        - "risk_score": Float between 0 and 1
    '''
    df['risk_flag'] = (df['component_A'] > 0.70) & (df['avg_pH'] < 6.9)

    # Score linearly increases if component_A > 0.70 or avg_pH < 6.9
    score = 0.5 * (df['component_A'] - 0.70) / 0.1 + 0.5 * (6.9 - df['avg_pH']) / 0.2
    df['risk_score'] = score.clip(lower=0, upper=1)

    return df

# ============================================
# Function: Export Markdown batch summary
# ============================================
def export_summary_report(df, output_path):
    '''
    Save a Markdown summary of batch risk outcomes.

    Args:
        df (pd.DataFrame): DataFrame with batch-level metrics.
        output_path (str): File path to save summary.
    '''
    try:
        with open(output_path, 'w') as f:
            f.write("# Batch Summary Report\n\n")
            for _, row in df.iterrows():
                f.write(f"## Batch {row['batch_id']}\n")
                f.write(f"- Date: {row['date']}\n")
                f.write(f"- Component A: {row['component_A']}\n")
                f.write(f"- Avg pH: {row['avg_pH']}\n")
                f.write(f"- Viability: {row['viability_pct']}%\n")
                f.write(f"- Risk Flag: {'YES' if row['risk_flag'] else 'NO'}\n\n")
        print("Markdown summary exported.")
    except Exception as e:
        print(f"Markdown export failed: {e}")

# ============================================
# Function: Append batch scores to master log
# ============================================
def append_to_master_log(df, log_path):
    '''
    Add scored batch-level rows to a running CSV log.

    Args:
        df (pd.DataFrame): Processed batch-level data.
        log_path (str): File path to cumulative log file.
    '''
    cols_to_save = ['batch_id', 'date', 'component_A', 'avg_pH', 'viability_pct', 'risk_flag', 'risk_score']
    new_data = df[cols_to_save]
    try:
        if os.path.exists(log_path):
            existing = pd.read_csv(log_path)
            combined = pd.concat([existing, new_data], ignore_index=True)
        else:
            combined = new_data
        combined.to_csv(log_path, index=False)
        print("Master log updated.")
    except Exception as e:
        print(f"Error writing master log: {e}")

# ============================================
# Function: Plot time trend of risk scores
# ============================================
def plot_risk_trend(log_path, plot_path):
    '''
    Plot time-series of batch risk scores from master log.

    Args:
        log_path (str): File path to cumulative log file.
        plot_path (str): Output image path for risk trend plot.
    '''
    try:
        df = pd.read_csv(log_path, parse_dates=['date'])
        df.sort_values('date', inplace=True)

        plt.figure(figsize=(10, 6))
        plt.plot(df['date'], df['risk_score'], marker='o', linestyle='-', label='Risk Score')
        plt.title('Batch Risk Score Over Time')
        plt.xlabel('Date')
        plt.ylabel('Risk Score (0–1)')
        plt.grid(True, linestyle='--', alpha=0.3)
        plt.tight_layout()
        plt.savefig(plot_path, dpi=300)
        plt.close()
        print("Risk trend plot saved.")
    except Exception as e:
        print(f"Failed to generate trend plot: {e}")

# ============================================
# Main Runner
# ============================================
def main():
    '''
    Main execution block: load files, merge data, score batches, export outputs.

    Edit input_dir as needed to reflect your file structure.
    '''
    # Update with your actual folder path. Use raw string if using Windows (e.g., r'C:\path\to\files')
    input_dir = '.'

    # Define input/output file paths
    batch_path = os.path.join(input_dir, 'example_batch_log.csv')
    qc_path = os.path.join(input_dir, 'example_qc_data.csv')
    coa_path = os.path.join(input_dir, 'example_coa.csv')
    output_md = os.path.join(input_dir, 'batch_summary_output.md')
    history_log = os.path.join(input_dir, 'batch_history_log.csv')
    risk_plot = os.path.join(input_dir, 'risk_trend_plot.png')

    # Run batch scoring pipeline
    batch_df = load_csv_file(batch_path, 'Batch Log')
    qc_df = load_csv_file(qc_path, 'QC Results')
    coa_df = load_csv_file(coa_path, 'COA Data')
    merged_df = merge_batch_data(batch_df, qc_df, coa_df)

    if not merged_df.empty:
        scored_df = apply_risk_rules(merged_df)
        export_summary_report(scored_df, output_md)
        append_to_master_log(scored_df, history_log)
        plot_risk_trend(history_log, risk_plot)
        print("Process complete.")
    else:
        print("No data to process.")

# Only run main() when executed directly, not imported
if __name__ == '__main__':
    main()
