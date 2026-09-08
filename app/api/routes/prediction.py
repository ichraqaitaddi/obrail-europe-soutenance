from pathlib import Path

import joblib
import pandas as pd

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field


router = APIRouter(
    prefix="/predict",
    tags=["Prediction IA"]
)


# ============================================================
# Chargement du modèle
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[3]
MODEL_PATH = BASE_DIR / "models_ml" / "random_forest.pkl"

print(f"Chemin du modèle : {MODEL_PATH}")
print(f"Modèle trouvé : {MODEL_PATH.exists()}")

try:
    model = joblib.load(MODEL_PATH)
except Exception as e:
    model = None
    print(f"Erreur lors du chargement du modèle : {e}")


# ============================================================
# Schéma de la requête
# ============================================================

class PredictionRequest(BaseModel):

    route_id: str
    agency_id: str
    route_type: int

    direction_id: str

    origin_stop_id: str
    destination_stop_id: str

    n_stops: int = Field(gt=0)

    departure_hour: int = Field(ge=0, le=23)
    departure_minute: int = Field(ge=0, le=59)

    distance_km: float = Field(ge=0)


# ============================================================
# Endpoint de prédiction
# ============================================================

@router.post("/")
def predict_duration(request: PredictionRequest):

    if model is None:
        raise HTTPException(
            status_code=500,
            detail="Le modèle IA n'a pas pu être chargé."
        )

    data = pd.DataFrame([{
        "route_id": request.route_id,
        "agency_id": request.agency_id,
        "route_type": request.route_type,
        "direction_id": request.direction_id,
        "origin_stop_id": request.origin_stop_id,
        "destination_stop_id": request.destination_stop_id,
        "n_stops": request.n_stops,
        "departure_hour": request.departure_hour,
        "departure_minute": request.departure_minute,
        "distance_km": request.distance_km,
    }])

    try:

        prediction = model.predict(data)[0]

        return {
            "predicted_duration_minutes": round(
                float(prediction),
                2
            )
        }

    except Exception as e:

        raise HTTPException(
            status_code=400,
            detail=f"Erreur lors de la prédiction : {str(e)}"
        )