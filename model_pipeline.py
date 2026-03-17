
import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, classification_report, confusion_matrix
import matplotlib.pyplot as plt

from data_analysis import full
import config


def prepare_data(df):

    df = df.sort_values(by=['Country', 'Year'])
    df[config.TARGET_NEXT_YEAR] = df.groupby('Country')[config.TARGET_BASE].shift(-1)

    cols_to_check = config.FEATURES + [config.TARGET_NEXT_YEAR]
    df_clean = df.dropna(subset=cols_to_check).copy()

    X = df_clean[config.FEATURES].copy()
    y = df_clean[config.TARGET_NEXT_YEAR]

    return X, y, df_clean

def preprocess_features(data):

    def scaling_symlog(data, columns):
        scaler = MinMaxScaler(feature_range=(0, 1))
        for col in columns:
            data[col] = np.sign(data[col]) * np.log1p(np.abs(data[col]))
            data[col] = scaler.fit_transform(data[[col]])
        return data

    def scaling(data, columns):
        scaler = MinMaxScaler(feature_range=(0, 1))
        for col in columns:
            data[col] = scaler.fit_transform(data[[col]])
        return data

    cols_full = ['gdp']
    cols_standard = [
        'press_free', 'freedom_index', 'absence_of_violence', 'civil_liberties',
        'gov_stability', 'human_rights', 'electoral_integrity'
    ]

    data = scaling_symlog(data, cols_full)
    data = scaling(data, cols_standard)

    return data

def classify_system_type(index):

    if index > 8.0:
        return "Full democracies"
    elif index > 6.0:
        return "Flawed democracies"
    elif index > 4.0:
        return "Hybrid regimes"
    else:
        return "Authoritarian regimes"

def classify_risk(delta_y):

    if delta_y <= config.CRISIS_THRESHOLD:
        return 1  #🔴
    elif delta_y >= config.IMPROVEMENT_THRESHOLD:
        return 2  #🔵
    else:
        return 0  #🟢


def evaluate_system(y_test, y_pred, eiu_current_test):
    """
    Step 4: Generating performance reports (ML + Strategy).
    """
    # A. Evaluating ML (Numerical Error)
    print("\n" + "=" * 55)
    print("1. NUMERICAL PRECISION (Regression)")
    print("=" * 55)
    print(f"Baseline MAE: {mean_absolute_error(y_test, y_baseline):.3f} EIU pts")
    print(f"XGBoost Model MAE:  {mean_absolute_error(y_test, y_pred):.3f} EIU pts")

    # B. Evaluating the Early Warning System (Classification)
    class_true = (y_test - eiu_current_test).apply(classify_risk)
    class_xgb = (pd.Series(y_pred, index=y_test.index) - eiu_current_test).apply(classify_risk)

    print("\n" + "=" * 55)
    print("2.STRATEGIC EFFECTIVENESS (Risk Classification)")
    print("=" * 55)
    print(classification_report(class_true, class_xgb, zero_division=0))
    print("\n🗺️ CONFUSION MATRIX (0: Stability, 1: Crisis, 2: Improvement):")
    print(confusion_matrix(class_true, class_xgb))

    # --- NEW ADDITION: REGIME CHANGE REPORT ---
    print("\n" + "=" * 55)
    print("🌍 3. GEOPOLITICAL REPORT (EIU Regime Changes)")
    print("=" * 55)

    # Translating current scores and predictions into categories
    system_today = eiu_current_test.apply(classify_system_type)
    system_tomorrow = pd.Series(y_pred, index=y_test.index).apply(classify_system_type)

    # Checking where the regime changed
    changes = system_today != system_tomorrow
    num_change = changes.sum()

    print(f"The model analyzed {len(y_test)} test cases.")
    print(f"It predicted a change in the official regime category in {num_change} cases.")

    # If there are any changes, let's show the top 5 examples!
    if num_change > 0:
        print("\nSample regime transfers captured by the model:")
        przyklady = pd.DataFrame({
            'Was': system_today[changes],
            'Will be': system_tomorrow[changes]
        }).head(5)
        print(przyklady.to_string())

def plot_feature_importance(model):

    print("\n🧠 Generating feature importance chart (XAI)...")
    importance_df = pd.DataFrame({
        'Feature': config.FEATURES,
        'Weight': model.feature_importances_
    }).sort_values(by='Weight', ascending=True)

    plt.figure(figsize=(10, 6))
    plt.barh(importance_df['Feature'], importance_df['Weight'], color='#2ca02c')
    plt.title("Importance of historical indicators for regime change (XGBoost)")
    plt.xlabel("Feature weight in decision trees")
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":

    X, y, df_clean = prepare_data(full)

    X_scaled_df = preprocess_features(X)

    year_limit = 2019

    X_train = X_scaled_df[df_clean['Year'] < year_limit]
    y_train = y[df_clean['Year'] < year_limit]

    X_test = X_scaled_df[df_clean['Year'] >= year_limit]
    y_test = y[df_clean['Year'] >= year_limit]

    y_baseline = df_clean.loc[X_test.index, config.TARGET_BASE]

    model = xgb.XGBRegressor(**config.XGB_PARAMS)
    model.fit(X_train, y_train)

    y_pred = np.clip(model.predict(X_test), 0, 10)

    evaluate_system(y_test, y_pred, y_baseline)
    plot_feature_importance(model)