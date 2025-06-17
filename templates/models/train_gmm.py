'''
train_gmm.py

Train a Gaussian Mixture Model (GMM) to discover unsupervised clusters in process data
and estimate per-cluster failure probability based on a downstream quality metric.

GMM identifies clusters in the normalized process feature space and evaluates how
frequently each cluster is associated with a failing quality metric.

Author: Josh Villanueva
'''

import pandas as pd
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler

# ============================================
# Function: Train Gaussian Mixture Model
# ============================================
def train_gmm(df, features, threshold, target_col, n_clusters=2):
    '''
    Train a GMM clustering model and estimate cluster-wise failure probabilities.

    Parameters:
    - df (pd.DataFrame): Dataset with process features and quality outcome
    - features (list): Columns representing process characteristics (inputs to clustering)
    - threshold (float): Threshold to define failure based on target_col values
    - target_col (str): Quality metric column to determine pass/fail
    - n_clusters (int): Number of clusters to find in the data (default = 2)

    Returns:
    - model (GaussianMixture): Trained GMM model
    - scaler (StandardScaler): Scaler used for feature normalization
    - df (pd.DataFrame): Input DataFrame with cluster and failure probability columns added
    - cluster_map (dict): Mapping of cluster_id → estimated failure probability

    Step-by-step:
    1. Select the feature columns and normalize them using StandardScaler.
       This ensures all features are on the same scale (mean=0, std=1) for clustering.
    2. Fit a GMM with n_clusters (default=2) to the normalized feature space.
       Each data point is assigned a cluster ID based on feature similarity.
    3. For each cluster, calculate the percentage of samples that fail based on target_col.
       This becomes the estimated failure probability for that cluster.
    4. The DataFrame is updated with per-batch cluster assignments and probabilities.
       A cluster → risk dictionary is also returned.
    '''
    # Step 1: Normalize feature space
    X = df[features].copy()
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Step 2: Train GMM (unsupervised probabilistic clustering)
    model = GaussianMixture(n_components=n_clusters, random_state=0)
    cluster_ids = model.fit_predict(X_scaled)
    df['gmm_cluster'] = cluster_ids

    # Step 3: Estimate failure probability within each cluster
    # This line computes the % of rows that failed in each cluster
    # .transform() maps the result back to the same shape as the original DataFrame
    df['gmm_p_failure'] = df.groupby('gmm_cluster')[target_col].transform(
        lambda x: (x < threshold).mean()
    )

    # This line creates a dictionary with cluster_id as key and P(failure) as value
    # .apply() computes once per group and returns a compact mapping
    cluster_map = df.groupby('gmm_cluster')[target_col].apply(
        lambda x: (x < threshold).mean()
    ).to_dict()

    return model, scaler, df, cluster_map

# ============================================
# Optional Test Block
# ============================================
if __name__ == '__main__':
    # Simulated example data
    sample_df = pd.DataFrame({
        'feature1': [1.1, 1.2, 1.0, 1.3, 2.5, 2.6],
        'feature2': [7.1, 6.8, 7.0, 7.2, 8.0, 8.1],
        'final_metric': [0.91, 0.92, 0.94, 0.88, 0.75, 0.72]
    })
    model, scaler, df_out, cluster_map = train_gmm(
        sample_df,
        features=['feature1', 'feature2'],
        threshold=0.9,
        target_col='final_metric',
        n_clusters=2  # You can adjust this if more failure modes are suspected
    )
    print("Cluster failure probabilities:", cluster_map)
