from pathlib import Path
import joblib


MODEL_PATH = (
    Path(__file__).resolve().parents[1]
    / "models_ml"
    / "random_forest.pkl"
)


def test_model_exists():
    """Vérifie que le modèle entraîné existe."""
    assert MODEL_PATH.exists(), (
        f"Modèle introuvable : {MODEL_PATH}"
    )


def test_model_can_be_loaded():
    """Vérifie que le modèle peut être chargé."""
    model = joblib.load(MODEL_PATH)

    assert model is not None


def test_model_has_predict():
    """Vérifie que le modèle possède une méthode de prédiction."""
    model = joblib.load(MODEL_PATH)

    assert hasattr(model, "predict")


def test_model_prediction_is_valid():
    """Vérifie que le modèle produit une prédiction valide."""
    model = joblib.load(MODEL_PATH)

    sample = {
        "route_id": ["FR_TEST"],
        "agency_id": ["1187"],
        "route_type": [2],
        "direction_id": ["0"],
        "origin_stop_id": ["STOP_ORIGIN"],
        "destination_stop_id": ["STOP_DEST"],
        "n_stops": [8],
        "departure_hour": [10],
        "departure_minute": [30],
        "distance_km": [100.0],
    }

    import pandas as pd

    X = pd.DataFrame(sample)

    prediction = model.predict(X)

    assert len(prediction) == 1
    assert prediction[0] > 0