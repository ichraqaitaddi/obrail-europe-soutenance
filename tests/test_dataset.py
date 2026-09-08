from pathlib import Path
import pandas as pd


# Chemin vers le dataset ML
DATASET_PATH = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "processed"
    / "dataset_ml.csv"
)


def test_dataset_exists():
    """Vérifie que le dataset ML existe."""
    assert DATASET_PATH.exists(), (
        f"Dataset introuvable : {DATASET_PATH}"
    )


def test_dataset_not_empty():
    """Vérifie que le dataset contient des données."""
    df = pd.read_csv(DATASET_PATH)

    assert len(df) > 0, "Le dataset est vide."


def test_required_columns():
    """Vérifie la présence des colonnes nécessaires au modèle."""
    df = pd.read_csv(DATASET_PATH)

    required_columns = {
        "trip_id",
        "route_id",
        "agency_id",
        "route_type",
        "direction_id",
        "origin_stop_id",
        "destination_stop_id",
        "n_stops",
        "departure_hour",
        "departure_minute",
        "distance_km",
        "duration_minutes",
    }

    missing_columns = required_columns - set(df.columns)

    assert not missing_columns, (
        f"Colonnes manquantes : {missing_columns}"
    )


def test_no_missing_values():
    """Vérifie qu'il n'y a pas de valeurs manquantes."""
    df = pd.read_csv(DATASET_PATH)

    assert df.isnull().sum().sum() == 0, (
        "Le dataset contient des valeurs manquantes."
    )


def test_duration_positive():
    """Vérifie que les durées sont strictement positives."""
    df = pd.read_csv(DATASET_PATH)

    assert (df["duration_minutes"] > 0).all(), (
        "Le dataset contient des durées nulles ou négatives."
    )


def test_n_stops_positive():
    """Vérifie que chaque trajet possède au moins un arrêt."""
    df = pd.read_csv(DATASET_PATH)

    assert (df["n_stops"] > 0).all(), (
        "Le dataset contient un nombre d'arrêts invalide."
    )


def test_distance_non_negative():
    """Vérifie que les distances sont positives ou nulles."""
    df = pd.read_csv(DATASET_PATH)

    assert (df["distance_km"] >= 0).all(), (
        "Le dataset contient une distance négative."
    )