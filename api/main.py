from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.predict import predict

app = FastAPI(
    title="Airbnb Price Predictor",
    description="Predict nightly Airbnb prices in Paris using XGBoost.",
    version="0.1.0",
)


class PredictRequest(BaseModel):
    # TODO: update fields to match actual features
    accommodates: int
    bedrooms: int
    bathrooms: float
    # add more features as needed


class PredictResponse(BaseModel):
    predicted_price: float


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict", response_model=PredictResponse)
def predict_price(request: PredictRequest):
    try:
        features = request.model_dump()
        price = predict(features)
        return PredictResponse(predicted_price=price)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
