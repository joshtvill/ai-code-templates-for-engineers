'''
risk_logic_generator.py

Train and compare two probabilistic models for batch risk scoring based on historical data.
Intended for use in process development, MSAT, or manufacturing analytics contexts.

Models:
- Gaussian Mixture Model (GMM) for unsupervised failure-prone clustering
- Logistic Regression for supervised probability of QC failure

Expected inputs:
- example_batch_log.csv
- example_qc_data.csv
- example_coa.csv

Author: Josh Villanueva
'''

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.mixture import GaussianMixture
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, accuracy_score
from sklearn.preprocessing import StandardScaler
import joblib
import json

# ============================================
# Function: Load CSV file into DataFrame
# Tip: Use this for loading batch logs, QC data, and COA files
# ============================================
def load_csv(file_path, label):
    try:
        df = pd.read_csv(file_path)
        print(f"Loaded {label}: {df.shape[0]} rows")
        return df
    except Exception as e:
        print(f"Error loading {label}: {e}")
        return pd.DataFrame()

# ============================================
# Function: Merge batch, QC, and COA datasets
# ============================================
def merge_data(batch_df, qc_df, coa_df):
    try:
        df = pd.merge(batch_df, qc_df, on='batch_id', how='inner')
        df = pd.merge(df, coa_df, on='supplier_lot', how='left')
        print(f"Merged data shape: {df.shape}")
        return df
    except Exception as e:
        print(f"Merge error: {e}")
        return pd.DataFrame()

# ============================================
# Function: Train GMM and return failure probabilities
# ============================================
def train_gmm(df, features, viability_col='viability_pct'):
    X = df[features].copy()
    scaler = StandardScaler()  # Scales features to mean=0, std=1 (important for models like GMM and Logistic Regression)
    X_scaled = scaler.fit_transform(X)

    gmm = GaussianMixture(n_components=2, random_state=0)  # You can try 3+ clusters if your data has more latent failure modes
    cluster_ids = gmm.fit_predict(X_scaled)
    df['gmm_cluster'] = cluster_ids

    # Estimate cluster-wise failure probability
    df['gmm_p_failure'] = df.groupby('gmm_cluster')[viability_col].transform(lambda x: (x < 70).mean())

    return gmm, scaler, df

# ============================================
# Function: Train Logistic Regression model
# ============================================
def train_logistic(df, features, viability_threshold, viability_col='viability_pct'):
    """
    Trains a logistic regression model to classify batches as fail/pass based on viability threshold.
    
    Args:
        df (pd.DataFrame): Merged batch dataset.
        features (list): Feature column names for training.
        viability_threshold (float): Threshold to define fail/pass.
        viability_col (str): Column name for viability %.

    Returns:
        model, scaler, df, auc, accuracy
    """
    df['label'] = (df[viability_col] < viability_threshold).astype(int)
    X = df[features]
    y = df['label']

    scaler = StandardScaler()  # Scales features to mean=0, std=1 (important for models like GMM and Logistic Regression)
    X_scaled = scaler.fit_transform(X)

    model = LogisticRegression()  # Can adjust with class_weight='balanced' if your dataset is imbalanced
    model.fit(X_scaled, y)

    y_prob = model.predict_proba(X_scaled)[:, 1]
    df['logreg_p_failure'] = y_prob

    auc = roc_auc_score(y, y_prob)
    acc = accuracy_score(y, model.predict(X_scaled))
    print(f"Logistic Model – AUC: {auc:.2f}, Accuracy: {acc:.2f}")

    return model, scaler, df, auc, acc

# ============================================
# Function: Plot model comparison and viability map
# ============================================
def plot_models(df, features, output_dir):
    import os
    import matplotlib.pyplot as plt

    x, y = features
    cmap = 'coolwarm'  # Blue (low) to Red (high) for visual contrast

    fig, axes = plt.subplots(1, 3, figsize=(18, 5), sharex=True, sharey=True)

    # --- Viability Percentage Plot ---
    sc0 = axes[0].scatter(df[x], df[y], c=df['viability_pct'], cmap=cmap, edgecolor='k')
    axes[0].set_title('Viability %')
    axes[0].set_xlabel(x)
    axes[0].set_ylabel(y)
    cbar0 = plt.colorbar(sc0, ax=axes[0])
    cbar0.set_label('Viability (%)')

    # --- GMM Predicted Failure Probability ---
    sc1 = axes[1].scatter(df[x], df[y], c=df['gmm_p_failure'], cmap=cmap, vmin=0, vmax=1, edgecolor='k')
    axes[1].set_title('GMM Risk (Unsupervised)')
    axes[1].set_xlabel(x)
    cbar1 = plt.colorbar(sc1, ax=axes[1])
    cbar1.set_label('GMM P(failure)')

    # --- Logistic Regression Failure Probability ---
    sc2 = axes[2].scatter(df[x], df[y], c=df['logreg_p_failure'], cmap=cmap, vmin=0, vmax=1, edgecolor='k')
    axes[2].set_title('Logistic Risk (Supervised)')
    axes[2].set_xlabel(x)
    cbar2 = plt.colorbar(sc2, ax=axes[2])
    cbar2.set_label('Logistic P(failure)')

    # Save and clean up
    plt.tight_layout()
    out_path = os.path.join(output_dir, 'model_comparison.png')
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Model comparison plot saved to: {out_path}")

# ============================================
# Function: Save model artifacts and metadata
# ============================================
def save_artifacts(gmm, gmm_scaler, logreg, logreg_scaler, features, auc, acc, output_dir):
    try:
        joblib.dump({'model': gmm, 'scaler': gmm_scaler}, os.path.join(output_dir, 'risk_model_gmm.pkl'))
        joblib.dump({'model': logreg, 'scaler': logreg_scaler}, os.path.join(output_dir, 'risk_model_logreg.pkl'))

        metadata = {
            'features_used': features,
            'logreg_auc': auc,
            'logreg_accuracy': acc
        }
        with open(os.path.join(output_dir, 'risk_model_metadata.json'), 'w') as f:
            json.dump(metadata, f, indent=2)
        print("Models and metadata saved.")
    except Exception as e:
        print(f"Save error: {e}")

# ============================================
# Main Runner
# Loads historical data, trains both models, and saves outputs
# ============================================
def main():

     # ===== USER: Update with your actual folder path. Use raw string if using Windows (e.g., r'C:\path\to\files')
    base_dir = r'C:\Users\villa\OneDrive\Documents\GitHub\ai-code-templates-for-engineers\case_studies\batch_summary_tool'
    hist_dir = os.path.join(base_dir, 'historical_data')
    out_dir = os.path.join(base_dir, 'output')

    batch = load_csv(os.path.join(hist_dir, 'example_batch_log.csv'), 'Batch Log')
    qc = load_csv(os.path.join(hist_dir, 'example_qc_data.csv'), 'QC Results')
    coa = load_csv(os.path.join(hist_dir, 'example_coa.csv'), 'COA Data')
    merged = merge_data(batch, qc, coa)

    if merged.empty:
        print("No data to process.")
        return
    
    # ===== USER: Update this value based on your process criteria.
    # Batches with viability > threshold will be labeled as 'pass' (1), others as 'fail' (0).
    # Threshold feeds into Logisitic Regression model training, if threshold does not partition data into two classes, model will not train and return an error.
    viability_threshold = 0.90  # <-- EDIT HERE as needed (e.g., 0.90 for 90% viability)

    # ===== USER: Modify these if using different features
    features = ['component_A', 'avg_pH']

    gmm, gmm_scaler, merged = train_gmm(merged, features)
    logreg, logreg_scaler, merged, auc, acc = train_logistic(merged, features, viability_threshold)

    plot_models(merged, features, out_dir)
    save_artifacts(gmm, gmm_scaler, logreg, logreg_scaler, features, auc, acc, out_dir)
    print("Risk logic generation complete.")

if __name__ == '__main__':
    main()
