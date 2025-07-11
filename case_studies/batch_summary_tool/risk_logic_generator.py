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
def train_gmm(df, features, viability_threshold, viability_col='viability_pct'):
    X = df[features].copy()
    scaler = StandardScaler()  # Scales features to mean=0, std=1 (important for models like GMM and Logistic Regression)
    X_scaled = scaler.fit_transform(X)

    gmm = GaussianMixture(n_components=2, random_state=0)  # You can try 3+ clusters if your data has more latent failure modes
    cluster_ids = gmm.fit_predict(X_scaled)
    df['gmm_cluster'] = cluster_ids

    # Estimate cluster-wise failure probability
    df['gmm_p_failure'] = df.groupby('gmm_cluster')[viability_col].transform(lambda x: (x < viability_threshold).mean())

    # Save cluster → failure probability mapping
    cluster_map = df.groupby('gmm_cluster')[viability_col].apply(lambda x: (x < viability_threshold).mean()).to_dict()

    return gmm, scaler, df, cluster_map

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
def plot_models(df, features, output_dir, logreg_model=None):
    import os
    import numpy as np
    import matplotlib.pyplot as plt

    x, y = features
    cmap_viab = 'viridis'
    cmap_risk = 'RdBu_r'

    fig, axes = plt.subplots(1, 3, figsize=(18, 5), sharex=True, sharey=True)

    # --- Viability Percentage Plot ---
    sc0 = axes[0].scatter(df[x], df[y], c=df['viability_pct'], cmap=cmap_viab, edgecolor='k')
    axes[0].set_title('Viability %')
    axes[0].set_xlabel(x)
    axes[0].set_ylabel(y)
    cbar0 = plt.colorbar(sc0, ax=axes[0])
    cbar0.set_label('Viability (%)')

    # --- GMM Predicted Failure Probability ---
    sc1 = axes[1].scatter(df[x], df[y], c=df['gmm_p_failure'], cmap=cmap_risk, vmin=0, vmax=1, edgecolor='k')
    axes[1].set_title('GMM Risk (Unsupervised)')
    axes[1].set_xlabel(x)
    cbar1 = plt.colorbar(sc1, ax=axes[1])
    cbar1.set_label('GMM P(failure)')

    # Annotate GMM clusters
    for cluster_id in sorted(df['gmm_cluster'].unique()):
        cluster_data = df[df['gmm_cluster'] == cluster_id]
        center_x = cluster_data[x].mean()
        center_y = cluster_data[y].mean()
        p_fail = cluster_data['gmm_p_failure'].iloc[0]
        axes[1].text(center_x, center_y, f'Cluster {cluster_id}\nP={p_fail:.2f}',
                     fontsize=9, ha='center', va='center',
                     bbox=dict(facecolor='white', edgecolor='gray', alpha=0.75))

    # --- Logistic Regression Failure Probability ---
    sc2 = axes[2].scatter(df[x], df[y], c=df['logreg_p_failure'], cmap=cmap_risk, vmin=0, vmax=1, edgecolor='k')
    axes[2].set_title('Logistic Risk (Supervised)')
    axes[2].set_xlabel(x)
    cbar2 = plt.colorbar(sc2, ax=axes[2])
    cbar2.set_label('Logistic P(failure)')

    # --- Add Decision Boundary if model is provided ---
    if logreg_model is not None:
        model = logreg_model['model']
        scaler = logreg_model['scaler']

        # Create a meshgrid across the feature space
        x_min, x_max = df[x].min() - 0.05, df[x].max() + 0.05
        y_min, y_max = df[y].min() - 0.05, df[y].max() + 0.05
        xx, yy = np.meshgrid(np.linspace(x_min, x_max, 300),
                             np.linspace(y_min, y_max, 300))
        grid = np.c_[xx.ravel(), yy.ravel()]
        grid_scaled = scaler.transform(grid)
        probs = model.predict_proba(grid_scaled)[:, 1].reshape(xx.shape)

        # Draw the 0.5 decision boundary
        contour = axes[2].contour(xx, yy, probs, levels=[0.5], colors='black', linewidths=1.5)
        contour.collections[0].set_label('Decision Boundary (P=0.5)')
        axes[2].legend(loc='upper right')

    # Save and clean up
    plt.tight_layout()
    out_path = os.path.join(output_dir, 'model_comparison.png')
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Model comparison plot saved to: {out_path}")

# ============================================
# Function: Save model artifacts and metadata
# ============================================
def save_artifacts(gmm, gmm_scaler, logreg, logreg_scaler, features, auc, acc, output_dir, cluster_map):
    try:
        # Save models with scalers
        joblib.dump({'model': gmm, 'scaler': gmm_scaler}, os.path.join(output_dir, 'risk_model_gmm.pkl'))
        joblib.dump({'model': logreg, 'scaler': logreg_scaler}, os.path.join(output_dir, 'risk_model_logreg.pkl'))

        # Save model metadata
        metadata = {
            'features_used': features,
            'logreg_auc': auc,
            'logreg_accuracy': acc
        }
        with open(os.path.join(output_dir, 'risk_model_metadata.json'), 'w') as f:
            json.dump(metadata, f, indent=2)

        # Save cluster-to-failure-probability mapping
        cluster_map_path = os.path.join(output_dir, 'gmm_cluster_map.json')
        with open(cluster_map_path, 'w') as f:
            json.dump(cluster_map, f, indent=2)

        print("Models, metadata, and cluster map saved.")

    except Exception as e:
        print(f"Save error: {e}")


# ============================================
# Main Runner
# Loads historical data, trains both models, and saves outputs
# ============================================
def main():

    # ===== USER: Update with your actual folder path. Use raw string if using Windows (e.g., r'C:\path\to\files')
    base_dir = r'C:\path\to\your\batch_summary_tool'
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
    # Threshold feeds into Logistic Regression model training.
    viability_threshold = 0.90  # <-- EDIT HERE as needed (e.g., 0.90 for 90% viability)

    # ===== USER: Modify these if using different features
    features = ['component_A', 'avg_pH']

    # Train GMM model and extract cluster risk mapping
    gmm, gmm_scaler, merged, cluster_map = train_gmm(merged, features, viability_threshold)

    # Train logistic regression
    logreg, logreg_scaler, merged, auc, acc = train_logistic(merged, features, viability_threshold)

    # Plot comparison and save outputs
    plot_models(merged, features, out_dir, logreg_model={'model': logreg, 'scaler': logreg_scaler})
    save_artifacts(gmm, gmm_scaler, logreg, logreg_scaler, features, auc, acc, out_dir, cluster_map)

    print("Risk logic generation complete.")

if __name__ == '__main__':
    main()
