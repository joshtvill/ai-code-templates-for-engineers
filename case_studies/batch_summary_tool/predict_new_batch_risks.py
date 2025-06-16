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
def apply_models(df, model_dict, features, method_label, flag_threshold=0.5, cluster_map=None):
    '''
    Predict P(failure) using a trained model and scaler.

    Args:
        df (pd.DataFrame): New batch data
        model_dict (dict): Contains 'model' and 'scaler'
        features (list): Input features for prediction
        method_label (str): Prefix to store results (e.g., 'gmm', 'logreg')
        cluster_map (dict): Optional – mapping of GMM cluster IDs to failure probabilities

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

            if cluster_map is not None:
                df['gmm_p_failure'] = df['gmm_cluster'].map(cluster_map)
            else:
                raise ValueError("Missing cluster_map input for GMM model.")

        else:  # Logistic regression
            p_failure = model.predict_proba(X_scaled)[:, 1]
            df['logreg_p_failure'] = p_failure

        # Apply generic threshold logic
        df[f'{method_label}_risk_flag'] = df[f'{method_label}_p_failure'] > flag_threshold

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

def plot_risk_trend(df, score_col, flag_col, output_path, threshold_line=None):
    '''
    Plot time-series of risk scores with color-coded flags and optional threshold line.
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

        # Plot threshold line
        if threshold_line is not None:
            plt.axhline(y=threshold_line, color='black', linestyle=':', linewidth=1)
            plt.text(df['date'].min(), threshold_line + 0.01,
                     f'Threshold = {threshold_line:.2f}',
                     fontsize=8, color='black', va='bottom')

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

    # ===== USER: Update flag threshold for risk scoring
    flag_thresh = 0.5  # Threshold for risk flagging

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
    cluster_map_path = os.path.join(output_dir, 'gmm_cluster_map.json')

    if not all(os.path.exists(p) for p in [gmm_path, logreg_path, cluster_map_path]):
        print("Missing one or more required model files.")
        return

    # Load models and GMM cluster risk mapping
    gmm_model = joblib.load(gmm_path)
    logreg_model = joblib.load(logreg_path)

    import json
    with open(cluster_map_path, 'r') as f:
        raw_map = json.load(f)
        gmm_cluster_map = {int(k): v for k, v in raw_map.items()}


    # Predict risk using both models
    df = apply_models(df, gmm_model, features, 'gmm', flag_threshold=flag_thresh, cluster_map=gmm_cluster_map)
    df = apply_models(df, logreg_model, features,'logreg', flag_threshold=flag_thresh)

    # Append to log
    history_log = os.path.join(output_dir, 'batch_history_log.csv')
    log_cols = ['batch_id', 'date', 'component_A', 'avg_pH',
                'gmm_p_failure', 'gmm_risk_flag',
                'logreg_p_failure', 'logreg_risk_flag']
    append_to_log(df, history_log, log_cols)

    # Save plots
    plot_risk_trend(df, 'gmm_p_failure', 'gmm_risk_flag',
                    os.path.join(output_dir, 'risk_trend_gmm.png'), threshold_line=flag_thresh)
    plot_risk_trend(df, 'logreg_p_failure', 'logreg_risk_flag',
                    os.path.join(output_dir, 'risk_trend_logreg.png'), threshold_line=flag_thresh)

    print("Risk scoring complete.")

if __name__ == '__main__':
    main()
