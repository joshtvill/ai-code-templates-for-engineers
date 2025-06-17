'''
apply_model_to_batch.py

Apply a trained model and scaler to new process batch data to infer probability of failure.
Supports both logistic regression and GMM-based risk scoring.

Intended for use in systems that need to assess batch risk before final QC results are available.

Author: Josh Villanueva
'''

import pandas as pd

# ============================================
# Function: Apply model to new data and score risk
# ============================================
def apply_model_to_batch(df, model_dict, features, method_label,
                         flag_threshold=0.5, cluster_map=None):
    '''
    Predict risk using a pre-trained model and process features.

    Parameters:
    - df (pd.DataFrame): New batch data
    - model_dict (dict): Contains 'model' and 'scaler' from training phase
    - features (list): Feature columns used during training
    - method_label (str): Used as prefix for column names (e.g., 'gmm', 'logreg')
    - flag_threshold (float): Threshold to flag batches as high risk
    - cluster_map (dict): For GMM only — maps cluster_id → failure probability

    Returns:
    - pd.DataFrame: Original df with added columns:
        - {method_label}_p_failure
        - {method_label}_risk_flag
        - gmm_cluster (if method is GMM)

    Notes:
    - GMM assigns a cluster ID and maps to failure probability.
    - Logistic regression outputs a direct probability of failure.
    '''
    try:
        X = df[features]
        X_scaled = model_dict['scaler'].transform(X)
        model = model_dict['model']

        if method_label == 'gmm':
            # GMM: Predict cluster IDs from feature space
            cluster_id = model.predict(X_scaled)
            df['gmm_cluster'] = cluster_id

            # Map cluster → risk probability
            if cluster_map is not None:
                df['gmm_p_failure'] = df['gmm_cluster'].map(cluster_map)
            else:
                raise ValueError("Missing cluster_map input for GMM model.")

        else:  # Supervised model like logistic regression
            p_failure = model.predict_proba(X_scaled)[:, 1]
            df[f'{method_label}_p_failure'] = p_failure

        # Flag high-risk batches based on threshold
        df[f'{method_label}_risk_flag'] = df[f'{method_label}_p_failure'] > flag_threshold

    except Exception as e:
        print(f"Error in {method_label} prediction: {e}")

    return df

# ============================================
# Optional Test Block
# ============================================
if __name__ == '__main__':
    # Simulate dummy new data
    new_df = pd.DataFrame({
        'feature1': [1.1, 1.3, 2.4],
        'feature2': [7.0, 6.9, 8.2]
    })

    # Simulated logistic regression model dict
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler

    train_df = pd.DataFrame({
        'feature1': [1.0, 1.2, 2.5, 2.6],
        'feature2': [6.9, 7.1, 8.0, 8.1]
    })
    scaler = StandardScaler()
    X_train = scaler.fit_transform(train_df)
    model = LogisticRegression().fit(X_train, [0, 0, 1, 1])

    model_dict = {'model': model, 'scaler': scaler}
    result_df = apply_model_to_batch(new_df, model_dict,
                                     features=['feature1', 'feature2'],
                                     method_label='logreg',
                                     flag_threshold=0.5)
    print(result_df)
