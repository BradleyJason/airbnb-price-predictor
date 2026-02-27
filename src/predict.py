import mlflow.xgboost
import pandas as pd


def load_model(model_uri: str):
    import os
    from dotenv import load_dotenv
    load_dotenv()
    import dagshub
    dagshub.init(repo_owner="BradleyJason", repo_name="airbnb-price-predictor", mlflow=True)
    return mlflow.xgboost.load_model(model_uri)


def predict(features: dict, model_uri: str = "models:/airbnb-price-predictor/Production"):
    model = load_model(model_uri)
    df = pd.DataFrame([features])
    prediction = model.predict(df)
    return float(prediction[0])


if __name__ == "__main__":
    sample = {
        # TODO: fill with real feature names and sample values
        "accommodates": 2,
        "bedrooms": 1,
        "bathrooms": 1,
    }
    price = predict(sample)
    print(f"Predicted price: €{price:.2f}")
