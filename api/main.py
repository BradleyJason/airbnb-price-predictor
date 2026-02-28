from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from src.predict import predict

app = FastAPI(
    title="Airbnb Price Predictor",
    description="Predict nightly Airbnb prices in Paris using XGBoost.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restrict to Vercel domain in production
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)


class PredictRequest(BaseModel):
    # All values must be label-encoded (matching sklearn LabelEncoder from preprocess.py)
    room_type: int               # 0=Entire home/apt, 1=Hotel room, 2=Private room, 3=Shared room
    neighbourhood_cleansed: int  # 0-19, alphabetical order
    accommodates: int
    bedrooms: int
    bathrooms: float
    number_of_reviews: int
    review_scores_rating: float
    availability_365: int
    minimum_nights: int


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
