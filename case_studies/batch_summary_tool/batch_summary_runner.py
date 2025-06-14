'''
batch_summary_runner.py

Main script for parsing and summarizing batch history data from multi-source logs.

This lightweight tool is intended for early triage, traceability audits, and
batch-level issue detection in manufacturing or lab-scale process environments.

Expected input: CSV files or log exports with step history, QC results, and/or tool messages.

Author: Josh Villanueva
'''

import pandas as pd
import os

# ============================================
# Load Batch Log File
# ============================================
def load_batch_logs(filepath):
    '''
    Load a batch log file into a DataFrame.

    Parameters:
    - filepath (str): Path to the batch history CSV file

    Returns:
    - pd.DataFrame: Parsed log data

    Notes:
    - This function expects a standard CSV format with headers.
    - Common options: encoding='utf-8', delimiter=','
    '''
    try:
        df = pd.read_csv(filepath)
        return df
    except Exception as e:
        print(f"Error loading file: {e}")
        return pd.DataFrame()

# ============================================
# Generate Batch Summary
# ============================================
def summarize_batch(df):
    '''
    Generate a summary of batch activity.

    Parameters:
    - df (pd.DataFrame): Raw batch log data

    Returns:
    - dict: Summary including step count, errors, aborts, and missing steps

    Notes:
    - This is a placeholder example. You may need to adjust logic
      depending on your log schema.
    '''
    summary = {}
    summary['total_steps'] = df.shape[0]

    if 'status' in df.columns:
        summary['aborted'] = df['status'].str.contains('abort', case=False).sum()
        summary['missing_steps'] = df['status'].isna().sum()
    else:
        summary['aborted'] = 'N/A'
        summary['missing_steps'] = 'N/A'

    return summary

# ============================================
# Export Markdown Summary
# ============================================
def export_summary(summary_dict, output_path):
    '''
    Save summary dictionary to a Markdown file.

    Parameters:
    - summary_dict (dict): Summary data
    - output_path (str): Path to save the output markdown file

    Notes:
    - You can adapt this to output CSV or plain text if needed.
    '''
    try:
        with open(output_path, 'w') as f:
            f.write("# Batch Summary Report\n\n")
            for k, v in summary_dict.items():
                f.write(f"- **{k}**: {v}\n")
    except Exception as e:
        print(f"Error writing summary: {e}")

# ============================================
# Main Runner
# ============================================
def main():
    '''
    Main execution block: load log file, generate summary, export to markdown.

    Edit input_csv and output_md as needed.
    '''
    input_csv = r'C:\Users\villa\OneDrive\Documents\GitHub\ai-code-templates-for-engineers\case_studies\batch_summary_tool\example_batch_log.csv'
    output_md = r'C:\Users\villa\OneDrive\Documents\GitHub\ai-code-templates-for-engineers\case_studies\batch_summary_tool\batch_summary_output.md'

    df = load_batch_logs(input_csv)
    if not df.empty:
        summary = summarize_batch(df)
        export_summary(summary, output_md)
        print("Batch summary saved.")
    else:
        print("No data to process.")

# Only run main() when executed directly, not imported
if __name__ == '__main__':
    main()
