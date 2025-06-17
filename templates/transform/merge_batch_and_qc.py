'''
merge_batch_and_qc.py

Merge batch log, QC results, and COA datasets using standard key columns.

This is a foundational step for joining process history, quality results,
and certificate metadata in manufacturing or MSAT data pipelines.

Author: Josh Villanueva
'''

import pandas as pd

# ============================================
# Function: Merge batch, QC, and COA datasets
# ============================================
def merge_batch_and_qc(batch_df, qc_df, coa_df):
    '''
    Join batch log with QC and COA data using shared keys.

    Parameters:
    - batch_df (pd.DataFrame): Batch metadata and input features
    - qc_df (pd.DataFrame): QC test results (e.g., viability, yield)
    - coa_df (pd.DataFrame): COA metadata by supplier lot

    Returns:
    - pd.DataFrame: Merged full dataset
    '''
    try:
        df = pd.merge(batch_df, qc_df, on='batch_id', how='inner')
        df = pd.merge(df, coa_df, on='supplier_lot', how='left')
        print(f"Merged dataset shape: {df.shape}")
        return df
    except Exception as e:
        print(f"Merge error: {e}")
        return pd.DataFrame()

# ============================================
# Optional Test Block
# ============================================
if __name__ == '__main__':
    # Dummy example DataFrames for testing merge
    batch_df = pd.DataFrame({'batch_id': [1, 2], 'supplier_lot': ['A', 'B']})
    qc_df = pd.DataFrame({'batch_id': [1, 2], 'viability_pct': [0.92, 0.85]})
    coa_df = pd.DataFrame({'supplier_lot': ['A', 'B'], 'cert_date': ['2024-01-01', '2024-01-02']})

    merged = merge_batch_and_qc(batch_df, qc_df, coa_df)
    print(merged)
