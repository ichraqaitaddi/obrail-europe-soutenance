from pathlib import Path

import pandas as pd
import numpy as np


# ============================================================
# 1. CHEMINS DU PROJET
# ============================================================

# Racine du projet ObRail Europe Soutenance
BASE_DIR = Path(__file__).resolve().parent.parent

# Dossier contenant les fichiers GTFS
GTFS_DIR = (
    BASE_DIR
    / "data"
    / "raw"
    / "Export_OpenData_SNCF_GTFS_NewTripId (1)"
)

# Dossier de sortie du dataset ML
OUTPUT_DIR = BASE_DIR / "data" / "processed"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Fichier final
OUTPUT_PATH = OUTPUT_DIR / "dataset_ml.csv"


# ============================================================
# 2. VÉRIFICATION DU DOSSIER GTFS
# ============================================================

if not GTFS_DIR.exists():
    raise FileNotFoundError(
        f"Le dossier GTFS est introuvable : {GTFS_DIR}"
    )

print("Lecture des fichiers GTFS...")


# ============================================================
# 3. LECTURE DES FICHIERS GTFS
# ============================================================

trips = pd.read_csv(
    GTFS_DIR / "trips.txt",
    dtype=str
)

routes = pd.read_csv(
    GTFS_DIR / "routes.txt",
    dtype=str
)

stops = pd.read_csv(
    GTFS_DIR / "stops.txt",
    dtype=str
)

stop_times = pd.read_csv(
    GTFS_DIR / "stop_times.txt",
    dtype=str
)


print(f"Nombre de trajets : {len(trips)}")
print(f"Nombre de stop_times : {len(stop_times)}")


# ============================================================
# 4. PRÉPARATION DES HORAIRES
# ============================================================

stop_times["stop_sequence"] = pd.to_numeric(
    stop_times["stop_sequence"],
    errors="coerce"
)

stop_times["arrival_time"] = pd.to_timedelta(
    stop_times["arrival_time"],
    errors="coerce"
)

stop_times["departure_time"] = pd.to_timedelta(
    stop_times["departure_time"],
    errors="coerce"
)


# Vérification des données manquantes
print("\nValeurs manquantes dans stop_times :")

print(
    f"arrival_time : "
    f"{stop_times['arrival_time'].isna().sum()}"
)

print(
    f"departure_time : "
    f"{stop_times['departure_time'].isna().sum()}"
)

print(
    f"stop_sequence : "
    f"{stop_times['stop_sequence'].isna().sum()}"
)


# ============================================================
# 5. TRI DES ARRÊTS
# ============================================================

stop_times = stop_times.sort_values(
    ["trip_id", "stop_sequence"]
)


# ============================================================
# 6. PREMIER ET DERNIER ARRÊT DE CHAQUE TRAJET
# ============================================================

first_stops = (
    stop_times
    .groupby("trip_id")
    .first()
    .reset_index()
)

last_stops = (
    stop_times
    .groupby("trip_id")
    .last()
    .reset_index()
)


# ============================================================
# 7. CALCUL DE LA DURÉE DU TRAJET
# ============================================================

duration = pd.DataFrame({
    "trip_id": first_stops["trip_id"],
    "origin_stop_id": first_stops["stop_id"],
    "destination_stop_id": last_stops["stop_id"],
    "departure_time": first_stops["departure_time"],
    "arrival_time": last_stops["arrival_time"]
})

duration["duration_minutes"] = (
    duration["arrival_time"]
    - duration["departure_time"]
).dt.total_seconds() / 60


# ============================================================
# 8. NOMBRE D'ARRÊTS PAR TRAJET
# ============================================================

n_stops = (
    stop_times
    .groupby("trip_id")
    .size()
    .reset_index(name="n_stops")
)

duration = duration.merge(
    n_stops,
    on="trip_id",
    how="left"
)


# ============================================================
# 9. INFORMATIONS DES TRAJETS
# ============================================================

dataset = trips[
    [
        "trip_id",
        "route_id",
        "service_id",
        "direction_id"
    ]
].copy()


dataset = dataset.merge(
    duration[
        [
            "trip_id",
            "origin_stop_id",
            "destination_stop_id",
            "duration_minutes",
            "n_stops",
            "departure_time"
        ]
    ],
    on="trip_id",
    how="inner"
)


# ============================================================
# 10. AJOUT DE L'AGENCE ET DU TYPE DE ROUTE
# ============================================================

routes_info = routes[
    [
        "route_id",
        "agency_id",
        "route_type"
    ]
].copy()


dataset = dataset.merge(
    routes_info,
    on="route_id",
    how="left"
)


# ============================================================
# 11. HEURE ET MINUTE DE DÉPART
# ============================================================

total_seconds = (
    dataset["departure_time"]
    .dt.total_seconds()
)

dataset["departure_hour"] = (
    total_seconds // 3600
).astype(int) % 24

dataset["departure_minute"] = (
    total_seconds // 60
).astype(int) % 60


# ============================================================
# 12. COORDONNÉES DES ARRÊTS
# ============================================================

stops_coordinates = stops[
    [
        "stop_id",
        "stop_lat",
        "stop_lon"
    ]
].copy()


stops_coordinates["stop_lat"] = pd.to_numeric(
    stops_coordinates["stop_lat"],
    errors="coerce"
)

stops_coordinates["stop_lon"] = pd.to_numeric(
    stops_coordinates["stop_lon"],
    errors="coerce"
)


# ============================================================
# 13. COORDONNÉES DE L'ORIGINE
# ============================================================

origin_coordinates = stops_coordinates.rename(
    columns={
        "stop_id": "origin_stop_id",
        "stop_lat": "origin_lat",
        "stop_lon": "origin_lon"
    }
)


dataset = dataset.merge(
    origin_coordinates,
    on="origin_stop_id",
    how="left"
)


# ============================================================
# 14. COORDONNÉES DE LA DESTINATION
# ============================================================

destination_coordinates = stops_coordinates.rename(
    columns={
        "stop_id": "destination_stop_id",
        "stop_lat": "destination_lat",
        "stop_lon": "destination_lon"
    }
)


dataset = dataset.merge(
    destination_coordinates,
    on="destination_stop_id",
    how="left"
)


# ============================================================
# 15. CALCUL DE LA DISTANCE
# ============================================================

def haversine(lat1, lon1, lat2, lon2):
    """
    Calcule la distance entre deux coordonnées GPS
    avec la formule de Haversine.

    Résultat : distance en kilomètres.
    """

    earth_radius = 6371.0

    lat1 = np.radians(lat1)
    lon1 = np.radians(lon1)

    lat2 = np.radians(lat2)
    lon2 = np.radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        np.sin(dlat / 2) ** 2
        + np.cos(lat1)
        * np.cos(lat2)
        * np.sin(dlon / 2) ** 2
    )

    c = 2 * np.arcsin(np.sqrt(a))

    return earth_radius * c


dataset["distance_km"] = haversine(
    dataset["origin_lat"],
    dataset["origin_lon"],
    dataset["destination_lat"],
    dataset["destination_lon"]
)


# ============================================================
# 16. EXTRACTION DE LA DATE DU TRAJET
# ============================================================

dataset["service_date"] = pd.to_datetime(
    dataset["trip_id"].str.extract(
        r"(20\d{6})"
    )[0],
    format="%Y%m%d",
    errors="coerce"
)


# ============================================================
# 17. GESTION DE DIRECTION_ID
# ============================================================

dataset["direction_id"] = (
    dataset["direction_id"]
    .fillna("UNKNOWN")
)


# ============================================================
# 18. SÉLECTION DES COLONNES FINALES
# ============================================================

dataset = dataset[
    [
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
        "service_date"
    ]
]


# ============================================================
# 19. CONTRÔLES DU DATASET
# ============================================================

print("\n" + "=" * 60)
print("CONTRÔLES DU DATASET ML")
print("=" * 60)

print(f"\nNombre de lignes : {len(dataset)}")
print(f"Nombre de colonnes : {len(dataset.columns)}")


print("\nValeurs manquantes :")
print(dataset.isna().sum())


print("\nStatistiques de la durée :")
print(
    dataset["duration_minutes"].describe()
)


print("\nStatistiques de la distance :")
print(
    dataset["distance_km"].describe()
)


print("\nNombre de trajets avec une durée négative :")
print(
    (dataset["duration_minutes"] < 0).sum()
)


print("\nNombre de trajets avec une durée nulle :")
print(
    (dataset["duration_minutes"] == 0).sum()
)


# ============================================================
# 20. SAUVEGARDE
# ============================================================

dataset.to_csv(
    OUTPUT_PATH,
    index=False
)


print("\n" + "=" * 60)
print("DATASET ML CRÉÉ AVEC SUCCÈS")
print("=" * 60)

print(f"\nFichier créé :")
print(OUTPUT_PATH)