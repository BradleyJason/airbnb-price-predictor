"""Integration tests for api/main.py — MLflow/DagsHub are fully mocked."""
from unittest.mock import MagicMock, patch
import numpy as np
import pytest
from httpx import AsyncClient, ASGITransport

from api.main import app

# ── Shared valid payload ──────────────────────────────────────────────────────
VALID_PAYLOAD = {
    "accommodates": 2,
    "bedrooms": 1,
    "bathrooms": 1.0,
}


@pytest.mark.asyncio
async def test_health_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_predict_endpoint_structure():
    """POST /predict with a mocked model — verifies response shape and type."""
    fake_model = MagicMock()
    # Model trained on log(price): return log(150) so expm1 gives ~149€
    fake_model.predict.return_value = np.array([np.log1p(150.0)])

    with patch("src.predict.mlflow.xgboost.load_model", return_value=fake_model), \
         patch("dagshub.init"), \
         patch("dotenv.load_dotenv"):

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/predict", json=VALID_PAYLOAD)

    assert response.status_code == 200
    body = response.json()
    assert "predicted_price" in body
    assert isinstance(body["predicted_price"], float)
    assert body["predicted_price"] > 0


@pytest.mark.asyncio
async def test_predict_endpoint_bad_payload():
    """Missing required fields → 422 Unprocessable Entity."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/predict", json={"accommodates": 2})

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_predict_endpoint_model_error_returns_500():
    """If the model raises, the API must return 500 with detail."""
    with patch("src.predict.mlflow.xgboost.load_model", side_effect=RuntimeError("model not found")), \
         patch("dagshub.init"), \
         patch("dotenv.load_dotenv"):

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/predict", json=VALID_PAYLOAD)

    assert response.status_code == 500
    assert "model not found" in response.json()["detail"]
