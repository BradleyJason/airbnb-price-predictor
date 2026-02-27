import os
import subprocess
import numpy as np
import mlflow
import mlflow.xgboost
import pandas as pd
from dotenv import load_dotenv
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score

load_dotenv()
import dagshub
dagshub.init(repo_owner="BradleyJason", repo_name="airbnb-price-predictor", mlflow=True)


def load_features(path: str):
    df = pd.read_csv(path)

    # Cap outliers at the 99th percentile
    price_cap = df["price"].quantile(0.99)
    df = df[df["price"] <= price_cap]

    X = df.drop(columns=["price"])
    y = df["price"]
    return X, y, price_cap


def train(data_path: str = "data/processed/listings_clean.csv"):
    X, y, price_cap = load_features(data_path)

    # Log-transform the target
    y = np.log1p(y)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    params = {
        "n_estimators": 500,
        "max_depth": 6,
        "learning_rate": 0.05,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "min_child_weight": 3,
    }

    mlflow.set_experiment("airbnb-price-predictor")

    with mlflow.start_run():
        mlflow.log_params(params)
        mlflow.log_param("log_transform", True)

        model = XGBRegressor(**params, random_state=42)
        model.fit(X_train, y_train)

        # Predict in log space, inverse-transform for real-scale metrics
        preds = model.predict(X_test)
        preds_real = np.expm1(preds)
        y_test_real = np.expm1(y_test)

        mae = mean_absolute_error(y_test_real, preds_real)
        r2 = r2_score(y_test_real, preds_real)

        mlflow.log_metric("mae", mae)
        mlflow.log_metric("r2", r2)
        mlflow.log_metric("price_cap", price_cap)

        git_commit = subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip()
        mlflow.set_tag("git_commit", git_commit)

        dvc_version = subprocess.check_output(["dvc", "status"]).decode().strip()
        mlflow.set_tag("dvc_data_version", dvc_version[:200])

        mlflow.xgboost.log_model(
            model,
            artifact_path="model",
            registered_model_name="airbnb-price-predictor",
        )

        print(f"MAE: {mae:.2f}€ | R2: {r2:.4f} | price_cap: {price_cap:.0f}€")

    return model


if __name__ == "__main__":
    train()
