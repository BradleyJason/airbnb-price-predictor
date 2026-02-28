"""
Set the 'champion' alias on a specific model version.
Usage: python scripts/set_alias.py [version]
Default version: 3
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

import mlflow
from mlflow.tracking import MlflowClient

os.environ["MLFLOW_TRACKING_USERNAME"] = os.environ["DAGSHUB_USERNAME"]
os.environ["MLFLOW_TRACKING_PASSWORD"] = os.environ["DAGSHUB_TOKEN"]
mlflow.set_tracking_uri(os.environ["MLFLOW_TRACKING_URI"])

client = MlflowClient()
model_name = "airbnb-price-predictor"
version = sys.argv[1] if len(sys.argv) > 1 else "3"

client.set_registered_model_alias(
    name=model_name,
    alias="champion",
    version=version,
)
print(f"Alias 'champion' set on v{version}")

# Verify
mv = client.get_model_version_by_alias(model_name, "champion")
print(f"Confirmed: models:/{model_name}@champion -> v{mv.version}")
