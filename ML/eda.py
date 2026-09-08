from pathlib import Path

import pandas as pd


# ============================================================
# 1. CHEMINS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATASET_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "dataset_ml.csv"
)


# ============================================================
# 2. CHARGEMENT DU DATASET
# ============================================================

print("Chargement du dataset ML...")

if not DATASET_PATH.exists():
    raise FileNotFoundError(
        f"Dataset introuvable : {DATASET_PATH}"
    )

df = pd.read_csv(DATASET_PATH)

print(f"Nombre de lignes : {len(df)}")
print(f"Nombre de colonnes : {len(df.columns)}")


# ============================================================
# 3. APERÇU
# ============================================================

print("\n" + "=" * 60)
print("APERÇU DU DATASET")
print("=" * 60)

print(df.head())


# ============================================================
# 4. TYPES DES VARIABLES
# ============================================================

print("\n" + "=" * 60)
print("TYPES DES VARIABLES")
print("=" * 60)

print(df.dtypes)


# ============================================================
# 5. VALEURS MANQUANTES
# ============================================================

print("\n" + "=" * 60)
print("VALEURS MANQUANTES")
print("=" * 60)

missing = df.isna().sum()

print(missing)


# ============================================================
# 6. DOUBLONS
# ============================================================

print("\n" + "=" * 60)
print("DOUBLONS")
print("=" * 60)

duplicates = df.duplicated().sum()

print(f"Nombre de lignes dupliquées : {duplicates}")


# ============================================================
# 7. STATISTIQUES DES VARIABLES NUMÉRIQUES
# ============================================================

print("\n" + "=" * 60)
print("STATISTIQUES DES VARIABLES NUMÉRIQUES")
print("=" * 60)

print(df.describe())


# ============================================================
# 8. ANALYSE DE LA VARIABLE CIBLE
# ============================================================

print("\n" + "=" * 60)
print("VARIABLE CIBLE : DURATION_MINUTES")
print("=" * 60)

duration = df["duration_minutes"]

print(f"Minimum : {duration.min():.2f} min")
print(f"Maximum : {duration.max():.2f} min")
print(f"Moyenne : {duration.mean():.2f} min")
print(f"Médiane : {duration.median():.2f} min")
print(f"Écart-type : {duration.std():.2f} min")

print("\nQuartiles :")

print(
    f"Q1 (25%) : {duration.quantile(0.25):.2f} min"
)

print(
    f"Q2 (50%) : {duration.quantile(0.50):.2f} min"
)

print(
    f"Q3 (75%) : {duration.quantile(0.75):.2f} min"
)


# ============================================================
# 9. VALEURS EXTRÊMES DE LA DURÉE
# ============================================================

print("\n" + "=" * 60)
print("VALEURS EXTRÊMES DE LA DURÉE")
print("=" * 60)

print(
    "Durées négatives :",
    (df["duration_minutes"] < 0).sum()
)

print(
    "Durées nulles :",
    (df["duration_minutes"] == 0).sum()
)

print(
    "Durées supérieures à 6 heures :",
    (df["duration_minutes"] > 360).sum()
)

print(
    "Durées supérieures à 10 heures :",
    (df["duration_minutes"] > 600).sum()
)


# ============================================================
# 10. ANALYSE DE LA DISTANCE
# ============================================================

print("\n" + "=" * 60)
print("ANALYSE DE LA DISTANCE")
print("=" * 60)

distance = df["distance_km"]

print(f"Minimum : {distance.min():.2f} km")
print(f"Maximum : {distance.max():.2f} km")
print(f"Moyenne : {distance.mean():.2f} km")
print(f"Médiane : {distance.median():.2f} km")

print("\nQuartiles :")

print(
    f"Q1 (25%) : {distance.quantile(0.25):.2f} km"
)

print(
    f"Q2 (50%) : {distance.quantile(0.50):.2f} km"
)

print(
    f"Q3 (75%) : {distance.quantile(0.75):.2f} km"
)


# ============================================================
# 11. DISTANCES ÉGALES À 0
# ============================================================

print("\n" + "=" * 60)
print("DISTANCES ÉGALES À 0")
print("=" * 60)

zero_distance = df[df["distance_km"] == 0]

print(
    f"Nombre de trajets avec distance = 0 : "
    f"{len(zero_distance)}"
)

if len(zero_distance) > 0:
    print("\nExemples :")
    print(
        zero_distance[
            [
                "trip_id",
                "origin_stop_id",
                "destination_stop_id",
                "n_stops",
                "duration_minutes"
            ]
        ].head(10)
    )


# ============================================================
# 12. CORRÉLATIONS
# ============================================================

print("\n" + "=" * 60)
print("CORRÉLATIONS AVEC LA DURÉE")
print("=" * 60)

numeric_columns = [
    "n_stops",
    "departure_hour",
    "departure_minute",
    "distance_km",
    "duration_minutes"
]

correlations = (
    df[numeric_columns]
    .corr()["duration_minutes"]
    .sort_values(ascending=False)
)

print(correlations)


# ============================================================
# 13. NOMBRE DE TRAJETS PAR AGENCE
# ============================================================

print("\n" + "=" * 60)
print("TRAJETS PAR AGENCE")
print("=" * 60)

agency_counts = (
    df["agency_id"]
    .value_counts()
)

print(agency_counts)


# ============================================================
# 14. NOMBRE DE ROUTES
# ============================================================

print("\n" + "=" * 60)
print("ROUTES")
print("=" * 60)

print(
    f"Nombre de routes différentes : "
    f"{df['route_id'].nunique()}"
)


# ============================================================
# 15. NOMBRE DE TRAJETS PAR TYPE DE ROUTE
# ============================================================

print("\n" + "=" * 60)
print("TRAJETS PAR TYPE DE ROUTE")
print("=" * 60)

route_type_counts = (
    df["route_type"]
    .value_counts()
    .sort_index()
)

print(route_type_counts)


# ============================================================
# 16. TRAJETS PAR HEURE DE DÉPART
# ============================================================

print("\n" + "=" * 60)
print("TRAJETS PAR HEURE DE DÉPART")
print("=" * 60)

departure_by_hour = (
    df["departure_hour"]
    .value_counts()
    .sort_index()
)

print(departure_by_hour)


# ============================================================
# 17. NOMBRE D'ARRÊTS
# ============================================================

print("\n" + "=" * 60)
print("NOMBRE D'ARRÊTS PAR TRAJET")
print("=" * 60)

print(
    df["n_stops"].describe()
)


# ============================================================
# 18. ANALYSE DE LA DATE
# ============================================================

print("\n" + "=" * 60)
print("PÉRIODE DES DONNÉES")
print("=" * 60)

df["service_date"] = pd.to_datetime(
    df["service_date"],
    errors="coerce"
)

print(
    f"Date minimale : {df['service_date'].min()}"
)

print(
    f"Date maximale : {df['service_date'].max()}"
)

print(
    f"Nombre de dates différentes : "
    f"{df['service_date'].nunique()}"
)


# ============================================================
# 19. RÉSUMÉ DE L'EDA
# ============================================================

print("\n" + "=" * 60)
print("RÉSUMÉ DE L'EDA")
print("=" * 60)

print(
    f"""
Dataset :
- {len(df)} trajets
- {len(df.columns)} variables
- {df['route_id'].nunique()} routes
- {df['agency_id'].nunique()} agences

Variable cible :
- durée moyenne : {duration.mean():.2f} min
- durée médiane : {duration.median():.2f} min
- durée min : {duration.min():.2f} min
- durée max : {duration.max():.2f} min

Distance :
- distance moyenne : {distance.mean():.2f} km
- distance médiane : {distance.median():.2f} km
- distance max : {distance.max():.2f} km

Qualité :
- valeurs manquantes : {df.isna().sum().sum()}
- doublons : {duplicates}
- durées négatives : {(duration < 0).sum()}
- durées nulles : {(duration == 0).sum()}
"""
)

print("\nEDA TERMINÉE.")