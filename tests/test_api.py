

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient
from app.api.main import app

from fastapi.testclient import TestClient

from app.api.main import app



client = TestClient(app)


def test_predict_endpoint_exists():
    """Vérifie que l'endpoint de prédiction est accessible."""

    response = client.post(
        "/predict/",
        json={
            "route_id": "FR_TEST",
            "agency_id": "1187",
            "route_type": 2,
            "direction_id": "0",
            "origin_stop_id": "STOP_ORIGIN",
            "destination_stop_id": "STOP_DEST",
            "n_stops": 8,
            "departure_hour": 10,
            "departure_minute": 30,
            "distance_km": 100.0,
        },
    )

    assert response.status_code == 200


def test_prediction_response_contains_duration():
    """Vérifie que l'API retourne une durée prédite."""

    response = client.post(
        "/predict/",
        json={
            "route_id": "FR_TEST",
            "agency_id": "1187",
            "route_type": 2,
            "direction_id": "0",
            "origin_stop_id": "STOP_ORIGIN",
            "destination_stop_id": "STOP_DEST",
            "n_stops": 8,
            "departure_hour": 10,
            "departure_minute": 30,
            "distance_km": 100.0,
        },
    )

    data = response.json()

    assert "predicted_duration_minutes" in data


def test_prediction_is_positive():
    """Vérifie que la prédiction retournée est positive."""

    response = client.post(
        "/predict/",
        json={
            "route_id": "FR_TEST",
            "agency_id": "1187",
            "route_type": 2,
            "direction_id": "0",
            "origin_stop_id": "STOP_ORIGIN",
            "destination_stop_id": "STOP_DEST",
            "n_stops": 8,
            "departure_hour": 10,
            "departure_minute": 30,
            "distance_km": 100.0,
        },
    )

    data = response.json()

    assert data["predicted_duration_minutes"] > 0


def test_invalid_request_is_rejected():
    """Vérifie que l'API rejette une donnée invalide."""

    response = client.post(
        "/predict/",
        json={
            "route_id": "FR_TEST",
            "agency_id": "1187",
            "route_type": 2,
            "direction_id": "0",
            "origin_stop_id": "STOP_ORIGIN",
            "destination_stop_id": "STOP_DEST",
            "n_stops": 0,
            "departure_hour": 10,
            "departure_minute": 30,
            "distance_km": 100.0,
        },
    )

    assert response.status_code == 422