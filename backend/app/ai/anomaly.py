import numpy as np


def detect_anomaly(historical_values: list[float], current_value: float, threshold: float = 2.0) -> dict:
    if len(historical_values) < 3:
        return {"is_anomaly": False, "z_score": 0.0, "direction": None}

    arr = np.array(historical_values)
    mean = float(np.mean(arr))
    std = float(np.std(arr))

    if std < 1e-9:
        return {"is_anomaly": False, "z_score": 0.0, "direction": None}

    z_score = (current_value - mean) / std
    is_anomaly = abs(z_score) > threshold

    return {
        "is_anomaly": is_anomaly,
        "z_score": round(z_score, 2),
        "direction": ("élevé" if z_score > 0 else "faible") if is_anomaly else None,
    }


def forecast_linear(values: list[float], labels: list[str], periods_ahead: int = 3) -> dict:
    if len(values) < 3:
        return {"forecast": [], "labels": [], "trend": "données insuffisantes", "slope": 0.0}

    from sklearn.linear_model import LinearRegression

    X = np.arange(len(values)).reshape(-1, 1)
    y = np.array(values)
    model = LinearRegression().fit(X, y)

    future_X = np.arange(len(values), len(values) + periods_ahead).reshape(-1, 1)
    forecast = model.predict(future_X).tolist()

    slope = float(model.coef_[0])
    if slope > 0.5:
        trend = "croissant"
    elif slope < -0.5:
        trend = "décroissant"
    else:
        trend = "stable"

    future_labels = [f"Prévision+{i+1}" for i in range(periods_ahead)]

    return {
        "forecast": [round(v, 2) for v in forecast],
        "labels": future_labels,
        "trend": trend,
        "slope": round(slope, 4),
    }
