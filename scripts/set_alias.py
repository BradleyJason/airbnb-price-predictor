"""
Set an alias on a specific model version in the MLflow Registry.
Usage: python scripts/set_alias.py [version] [alias]
Defaults: version=3, alias=champion
Examples:
  python scripts/set_alias.py 4 candidate
  python scripts/set_alias.py 4 champion
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
alias   = sys.argv[2] if len(sys.argv) > 2 else "champion"

client.set_registered_model_alias(
    name=model_name,
    alias=alias,
    version=version,
)
print(f"Alias '{alias}' set on v{version}")

# Verify
mv = client.get_model_version_by_alias(model_name, alias)
print(f"Confirmed: models:/{model_name}@{alias} -> v{mv.version}")
