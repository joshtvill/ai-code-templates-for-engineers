'''
train_logistic_regression.py

Train a logistic regression model to classify binary outcomes based on process data.

This template is intended for evaluating whether upstream process features can predict
a downstream quality metric such as yield, viability, purity, or similar.

Typical use case: Assess how well process variables correlate with final pass/fail outcomes.

Author: Josh Villanueva
'''

import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score, accuracy_score

# ============================================
# Function: Train logistic regression model
# ============================================
def train_logistic_regression(df, features, threshold, target_col):
    '''
    Train a logistic regression model and evaluate performance.

    Parameters:
    - df (pd.DataFrame): Dataset including features and a quality outcome column
    - features (list): Process data columns used as model inputs
                       (these are the predictors to be normalized and used in training)
    - threshold (float): Value to define binary pass/fail label
    - target_col (str): Column name containing the numeric quality outcome

    Returns:
    - model (LogisticRegression): Fitted logistic regression model object
    - scaler (StandardScaler): Scaler used to normalize features during training
    - df (pd.DataFrame): Original DataFrame with added 'logreg_p_failure' column
    - auc (float): Area under ROC curve (model ranking performance)
    - accuracy (float): Fraction of correct pass/fail predictions

    Step-by-step:
    1. Create binary labels by comparing the target column to a threshold.
       Rows below threshold are labeled 1 (fail), others 0 (pass).
    2. Normalize the feature columns using StandardScaler (mean=0, std=1).
    3. Fit a logistic regression model using the scaled features and binary labels.
    4. Predict probability of failure and store results in the original DataFrame.
    5. Evaluate model performance using AUC and accuracy.
    '''
    # Step 1: Create binary label for classification
    df['label'] = (df[target_col] < threshold).astype(int)

    # Step 2: Subset and scale feature data
    X = df[features]
    y = df['label']
    scaler = StandardScaler()  # Normalizes feature values to mean=0, std=1
    X_scaled = scaler.fit_transform(X)

    # Step 3: Train the logistic regression model
    model = LogisticRegression()
    model.fit(X_scaled, y)

    # Step 4: Predict probability of failure (P=1)
    y_prob = model.predict_proba(X_scaled)[:, 1]
    df['logreg_p_failure'] = y_prob

    # Step 5: Evaluate model performance
    auc = roc_auc_score(y, y_prob)  # Measures ranking ability (ideal = 1.0)
    accuracy = accuracy_score(y, model.predict(X_scaled))  # Proportion of correct classifications

    print(f"Logistic Model – AUC: {auc:.3f}, Accuracy: {accuracy:.3f}")

    return model, scaler, df, auc, accuracy

# ============================================
# Optional Test Block
# ============================================
if __name__ == '__main__':
    # Simulated example: predict outcome from two features
    sample_df = pd.DataFrame({
        'feature1': [1.1, 1.2, 1.0, 1.3],
        'feature2': [7.1, 6.8, 7.0, 7.2],
        'final_metric': [0.91, 0.88, 0.94, 0.85]
    })
    model, scaler, df_out, auc, acc = train_logistic_regression(
        sample_df,
        features=['feature1', 'feature2'],
        threshold=0.9,
        target_col='final_metric'
    )
