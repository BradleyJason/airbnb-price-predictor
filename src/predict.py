import mlflow.xgboost
import numpy as np
import pandas as pd


def load_model(model_uri: str):
    import os
    from dotenv import load_dotenv
    load_dotenv()
    os.environ["MLFLOW_TRACKING_USERNAME"] = os.environ.get("DAGSHUB_USERNAME", "")
    os.environ["MLFLOW_TRACKING_PASSWORD"] = os.environ.get("DAGSHUB_TOKEN", "")
    mlflow.set_tracking_uri(os.environ.get("MLFLOW_TRACKING_URI", ""))
    return mlflow.xgboost.load_model(model_uri)


FEATURE_ORDER = [
    "room_type", "neighbourhood_cleansed", "accommodates",
    "bedrooms", "bathrooms", "number_of_reviews",
    "review_scores_rating", "availability_365", "minimum_nights",
]


def predict(features: dict, model_uri: str = "models:/airbnb-price-predictor@champion"):
    model = load_model(model_uri)
    df = pd.DataFrame([features])[FEATURE_ORDER]
    log_prediction = model.predict(df)
    # Model was trained on log1p(price) — apply inverse transform
    return float(np.expm1(log_prediction[0]))


if __name__ == "__main__":
    sample = {
        "room_type": 0,
        "neighbourhood_cleansed": 7,
        "accommodates": 2,
        "bedrooms": 1,
        "bathrooms": 1.0,
        "number_of_reviews": 20,
        "review_scores_rating": 4.5,
        "availability_365": 120,
        "minimum_nights": 2,
    }
    price = predict(sample)
    print(f"Predicted price: €{price:.2f}")
