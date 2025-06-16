'''
predict_new_batch_risks.py

Apply trained GMM and logistic regression models to new batch data
and assess risk without access to final QC results.

Generates time-series plots of risk scores to visualize emerging trends.

Expected inputs:
- new_batch_log.csv
- new_coa.csv
- Saved models from Part 1: risk_model_gmm.pkl, risk_model_logreg.pkl

Author: Josh Villanueva
'''

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import joblib

# ============================================
# Function: Load CSV file
# ============================================
def load_csv_file(file_path, file_type='generic'):
    '''
    Load a CSV file into a DataFrame.
    '''
    try:
        df = pd.read_csv(file_path)
        print(f"Loaded {file_type}: {df.shape[0]} rows")
        return df
    except Exception as e:
        print(f"Failed to load {file_type} file: {e}")
        return pd.DataFrame()

# ============================================
# Function: Merge new batch and COA data
# ============================================
def merge_new_data(batch_df, coa_df):
    '''
    Join batch log with COA details using shared supplier_lot key.
    '''
    try:
        df = pd.merge(batch_df, coa_df, on='supplier_lot', how='left')
        print(f"Merged test data shape: {df.shape}")
        return df
    except Exception as e:
        print(f"Merge error: {e}")
        return pd.DataFrame()

# ============================================
# Function: Apply risk models to new data
# ============================================
def apply_models(df, model_dict, features, method_label):
    '''
    Predict P(failure) using a trained model and scaler.

    Args:
        df (pd.DataFrame): New batch data
        model_dict (dict): Contains 'model' and 'scaler'
        features (list): Input features for prediction
        method_label (str): Prefix to store results (e.g., 'gmm', 'logreg')

    Adds:
        df[f'{method_label}_p_failure']
        df[f'{method_label}_risk_flag']
    '''
    try:
        X = df[features]
        X_scaled = model_dict['scaler'].transform(X)
        model = model_dict['model']

        if method_label == 'gmm':
            cluster_id = model.predict(X_scaled)
            df['gmm_cluster'] = cluster_id

            # Manually define risk probabilities per cluster based on training data
            # (Adjust these if your cluster IDs map differently)
            cluster_risk_map = {0: 0.2, 1: 0.85}  # Example: cluster 1 has higher failure risk
            df['gmm_p_failure'] = df['gmm_cluster'].map(cluster_risk_map)
        else:
            p_failure = model.predict_proba(X_scaled)[:, 1]
            df['logreg_p_failure'] = p_failure

        # Apply generic threshold logic
        df[f'{method_label}_risk_flag'] = df[f'{method_label}_p_failure'] > 0.75
    except Exception as e:
        print(f"Error in {method_label} prediction: {e}")

    return df

# ============================================
# Function: Append new data to master log
# ============================================
def append_to_log(df, log_path, features_to_log):
    '''
    Add newly scored batches to cumulative CSV.
    '''
    new_data = df[features_to_log]
    try:
        if os.path.exists(log_path):
            existing = pd.read_csv(log_path)
            combined = pd.concat([existing, new_data], ignore_index=True)
        else:
            combined = new_data
        combined.to_csv(log_path, index=False)
        print("Updated master log.")
    except Exception as e:
        print(f"Write error: {e}")

# ============================================
# Function: Plot time series of risk scores
# ============================================
def plot_risk_trend(df, score_col, flag_col, output_path):
    '''
    Plot time-series of risk scores with color-coded flags.
    '''
    try:
        df['date'] = pd.to_datetime(df['date'])
        df.sort_values('date', inplace=True)

        colors = df[flag_col].map({True: 'red', False: 'blue'})
        plt.figure(figsize=(10, 6))
        plt.scatter(df['date'], df[score_col], c=colors)
        plt.xlabel('Date')
        plt.ylabel('Risk Score')
        plt.title(f'Risk Score Over Time – {score_col}')
        plt.grid(True, linestyle='--', alpha=0.3)
        plt.xticks(rotation=90)
        plt.tight_layout()
        plt.savefig(output_path, dpi=300)
        plt.close()
        print(f"Saved risk trend plot: {output_path}")
    except Exception as e:
        print(f"Trend plot failed: {e}")

# ============================================
# Main Runner
# ============================================
def main():
    '''
    Main execution block: load new batches, apply both models, export outputs.

    Edit base_dir to match your file structure.
    '''
    # ===== USER: Update base folder for your setup
    base_dir = r'C:\Users\villa\OneDrive\Documents\GitHub\ai-code-templates-for-engineers\case_studies\batch_summary_tool'

    test_dir = os.path.join(base_dir, 'test_data')
    output_dir = os.path.join(base_dir, 'output')

    # Load new batch and COA
    batch_path = os.path.join(test_dir, 'Test_Batch_Log.csv')
    coa_path = os.path.join(test_dir, 'Test_COA_Data.csv')

    batch_df = load_csv_file(batch_path, 'Test Batch Log')
    coa_df = load_csv_file(coa_path, 'Test COA')
    df = merge_new_data(batch_df, coa_df)

    if df.empty:
        print("No test data to process.")
        return

    # ===== USER: Match features to model training inputs
    features = ['component_A', 'avg_pH']

    # ===== Check that model files exist before loading
    gmm_path = os.path.join(output_dir, 'risk_model_gmm.pkl')
    logreg_path = os.path.join(output_dir, 'risk_model_logreg.pkl')

    if not os.path.exists(gmm_path):
        print(f"Missing GMM model: {gmm_path}")
    if not os.path.exists(logreg_path):
        print(f"Missing Logistic Regression model: {logreg_path}")
    if not os.path.exists(gmm_path) or not os.path.exists(logreg_path):
        print("Aborting. Please generate models with risk_logic_generator.py.")
        return

    # Load models if files are present
    gmm_model = joblib.load(gmm_path)
    logreg_model = joblib.load(logreg_path)

    # Predict risk using both models
    df = apply_models(df, gmm_model, features, 'gmm')
    df = apply_models(df, logreg_model, features, 'logreg')

    # Append to log
    history_log = os.path.join(output_dir, 'batch_history_log.csv')
    log_cols = ['batch_id', 'date', 'component_A', 'avg_pH',
                'gmm_p_failure', 'gmm_risk_flag',
                'logreg_p_failure', 'logreg_risk_flag']
    append_to_log(df, history_log, log_cols)

    # Save plots
    plot_risk_trend(df, 'gmm_p_failure', 'gmm_risk_flag',
                    os.path.join(output_dir, 'risk_trend_gmm.png'))
    plot_risk_trend(df, 'logreg_p_failure', 'logreg_risk_flag',
                    os.path.join(output_dir, 'risk_trend_logreg.png'))

    print("Risk scoring complete.")

if __name__ == '__main__':
    main()
