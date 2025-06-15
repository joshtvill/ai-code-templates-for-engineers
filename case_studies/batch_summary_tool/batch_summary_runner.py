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
# Function: Apply rule-based risk flag
# ============================================
def apply_risk_rules(df):
    '''
    Add binary flags for high-risk batches using simple rule logic.

    Current rule:
        component_A > 0.70 AND avg_pH < 6.9

    Adds:
        "risk_flag" column (True/False)
        "risk_score" column (0 or 1)
    '''
    df['risk_flag'] = (df['component_A'] > 0.70) & (df['avg_pH'] < 6.9)
    df['risk_score'] = df['risk_flag'].astype(int)
    return df

# ============================================
# Function: Export Markdown batch summary
# ============================================
def export_summary_report(df, output_path):
    '''
    Generate and save a Markdown report summarizing batch-level outcomes.

    Args:
        df (pd.DataFrame): DataFrame with batch-level metrics and risk flags.
        output_path (str): File path to save the .md report.

    MATLAB analogy:
        >> writetable(T, 'summary.md');
    '''
    try:
        with open(output_path, 'w') as f:
            f.write("# Batch Summary Report\n\n")
            for _, row in df.iterrows():
                f.write(f"## Batch {row['batch_id']}\n")
                f.write(f"- Component A: {row['component_A']}\n")
                f.write(f"- Avg pH: {row['avg_pH']}\n")
                f.write(f"- Viability: {row['viability_pct']}%\n")
                f.write(f"- Risk Flag: {'YES' if row['risk_flag'] else 'NO'}\n\n")
        print("Markdown summary exported.")
    except Exception as e:
        print(f"Markdown export failed: {e}")

# ============================================
# Function: Append batch results to history log
# ============================================
def append_to_master_log(df, log_path):
    '''
    Append batch-level risk scores to a cumulative history log.

    Args:
        df (pd.DataFrame): Scored batch-level data.
        log_path (str): File path to master history CSV.
    '''
    cols_to_save = ['batch_id', 'component_A', 'avg_pH', 'viability_pct', 'risk_flag', 'risk_score']
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
# Main Runner
# ============================================
def main():
    '''
    Main execution block: load files, merge data, score batches, export outputs.

    Edit input_csv and output_md as needed.
    '''
    # Update with your actual file paths. If using Windows paths, use raw string (r'path\to\file.csv')
    # Example: batch_path = r'C:\path\to\example_batch_log.csv'
    batch_path = 'example_batch_log.csv'
    qc_path = 'example_qc_data.csv'
    coa_path = 'example_coa.csv'
    output_md = 'batch_summary_output.md'
    history_log = 'batch_history_log.csv'

    # Run batch scoring pipeline
    batch_df = load_csv_file(batch_path, 'Batch Log')
    qc_df = load_csv_file(qc_path, 'QC Results')
    coa_df = load_csv_file(coa_path, 'COA Data')
    merged_df = merge_batch_data(batch_df, qc_df, coa_df)

    if not merged_df.empty:
        scored_df = apply_risk_rules(merged_df)
        export_summary_report(scored_df, output_md)
        append_to_master_log(scored_df, history_log)
        print("Process complete.")
    else:
        print("No data to process.")

# Only run main() when executed directly, not imported
if __name__ == '__main__':
    main()
