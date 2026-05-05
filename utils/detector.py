"""
detector.py — ML anomaly detection logic.
Supported algorithms: Isolation Forest (default), One-Class SVM, Local Outlier Factor.
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM
from sklearn.neighbors import LocalOutlierFactor
from sklearn.preprocessing import StandardScaler


ALGORITHMS = {
    "isolation_forest": "Isolation Forest",
    "one_class_svm": "One-Class SVM",
    "lof": "Local Outlier Factor",
}


def run_detection(df: pd.DataFrame, selected_columns: list[str], algorithm: str = "isolation_forest", contamination: float = 0.05) -> dict:
    """
    Run anomaly detection on `selected_columns` of `df`.

    Returns a dict with:
        - df_result  : original df + 'Anomaly_Score', 'Prediction', 'Status'
        - summary    : stats dict
        - chart_data : data ready for Chart.js
    """
    features = df[selected_columns].dropna()
    X = features.values

    # Standardise features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Train model
    model = _build_model(algorithm, contamination)
    if algorithm == "lof":
        predictions = model.fit_predict(X_scaled)
        scores = -model.negative_outlier_factor_
    else:
        model.fit(X_scaled)
        predictions = model.predict(X_scaled)
        scores = model.score_samples(X_scaled) if hasattr(model, "score_samples") else np.zeros(len(X))

    # Build result dataframe aligned to original index
    result_df = df.copy()
    result_df = result_df.loc[features.index]  # keep only rows without NaN
    result_df["Anomaly_Score"] = np.round(scores, 4)
    result_df["Prediction"] = predictions          # 1 = normal, -1 = anomaly
    result_df["Status"] = result_df["Prediction"].map({1: "Normal", -1: "Anomaly"})

    # Summary stats
    total = len(result_df)
    anomaly_count = int((result_df["Prediction"] == -1).sum())
    normal_count = total - anomaly_count
    anomaly_pct = round(anomaly_count / total * 100, 2)

    summary = {
        "total_rows": total,
        "normal_count": normal_count,
        "anomaly_count": anomaly_count,
        "anomaly_percentage": anomaly_pct,
        "algorithm_used": ALGORITHMS.get(algorithm, algorithm),
        "columns_used": selected_columns,
        "contamination": contamination,
    }

    # Chart.js data
    chart_data = _build_chart_data(result_df, selected_columns, normal_count, anomaly_count)

    return {
        "df_result": result_df,
        "summary": summary,
        "chart_data": chart_data,
    }


def _build_model(algorithm: str, contamination: float):
    if algorithm == "one_class_svm":
        nu = min(max(contamination, 0.001), 0.5)
        return OneClassSVM(nu=nu, kernel="rbf", gamma="scale")
    elif algorithm == "lof":
        return LocalOutlierFactor(n_neighbors=20, contamination=contamination)
    else:  # default: isolation_forest
        return IsolationForest(contamination=contamination, random_state=42, n_estimators=100)


def _build_chart_data(df: pd.DataFrame, columns: list[str], normal_count: int, anomaly_count: int) -> dict:
    """Prepare all chart payloads for the frontend."""

    normal_df = df[df["Status"] == "Normal"]
    anomaly_df = df[df["Status"] == "Anomaly"]

    # Scatter: first two selected columns (or duplicate first if only one)
    x_col = columns[0]
    y_col = columns[1] if len(columns) > 1 else columns[0]

    scatter = {
        "normal": {
            "x": normal_df[x_col].tolist(),
            "y": normal_df[y_col].tolist(),
        },
        "anomaly": {
            "x": anomaly_df[x_col].tolist(),
            "y": anomaly_df[y_col].tolist(),
        },
        "x_label": x_col,
        "y_label": y_col,
    }

    # Line: anomaly score over index
    line = {
        "labels": list(range(len(df))),
        "scores": df["Anomaly_Score"].tolist(),
        "statuses": df["Status"].tolist(),
    }

    # Pie: normal vs anomaly
    pie = {
        "labels": ["Normal", "Anomaly"],
        "values": [normal_count, anomaly_count],
    }

    # Distribution: histogram bins for each selected column
    distributions = {}
    for col in columns[:4]:  # cap at 4 columns
        values = df[col].dropna().tolist()
        distributions[col] = values

    return {
        "scatter": scatter,
        "line": line,
        "pie": pie,
        "distributions": distributions,
    }
