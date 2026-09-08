from pathlib import Path

import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


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

df = pd.read_csv(DATASET_PATH)

df["service_date"] = pd.to_datetime(
    df["service_date"]
)

print(f"Nombre total de trajets : {len(df)}")


# ============================================================
# 3. TRI CHRONOLOGIQUE
# ============================================================

df = df.sort_values(
    "service_date"
).reset_index(drop=True)


# ============================================================
# 4. TRAIN / TEST TEMPOREL
# ============================================================

unique_dates = sorted(
    df["service_date"].unique()
)

split_index = int(
    len(unique_dates) * 0.80
)

cutoff_date = unique_dates[split_index]

train_df = df[
    df["service_date"] < cutoff_date
].copy()

test_df = df[
    df["service_date"] >= cutoff_date
].copy()


print("\n" + "=" * 60)
print("SÉPARATION TRAIN / TEST")
print("=" * 60)

print(f"Date de coupure : {cutoff_date}")

print(
    f"Train : {len(train_df)} trajets"
)

print(
    f"Test  : {len(test_df)} trajets"
)

print(
    f"Train : {train_df['service_date'].min().date()} "
    f"→ {train_df['service_date'].max().date()}"
)

print(
    f"Test  : {test_df['service_date'].min().date()} "
    f"→ {test_df['service_date'].max().date()}"
)


# ============================================================
# 5. VARIABLES
# ============================================================

TARGET = "duration_minutes"

FEATURES = [
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
]


X_train = train_df[FEATURES]
y_train = train_df[TARGET]

X_test = test_df[FEATURES]
y_test = test_df[TARGET]


# ============================================================
# 6. VARIABLES CATÉGORIELLES ET NUMÉRIQUES
# ============================================================

CATEGORICAL_FEATURES = [
    "route_id",
    "agency_id",
    "route_type",
    "direction_id",
    "origin_stop_id",
    "destination_stop_id",
]

NUMERIC_FEATURES = [
    "n_stops",
    "departure_hour",
    "departure_minute",
    "distance_km",
]


# ============================================================
# 7. PRÉTRAITEMENT
# ============================================================

preprocessor = ColumnTransformer(
    transformers=[
        (
            "categorical",
            OneHotEncoder(
                handle_unknown="ignore"
            ),
            CATEGORICAL_FEATURES,
        ),
        (
            "numeric",
            "passthrough",
            NUMERIC_FEATURES,
        ),
    ]
)


# ============================================================
# 8. FONCTION D'ÉVALUATION
# ============================================================

def evaluate_model(
    model_name,
    model,
):
    """
    Entraîne et évalue un modèle.
    """

    print("\n" + "=" * 60)
    print(model_name)
    print("=" * 60)

    model.fit(
        X_train,
        y_train
    )

    predictions = model.predict(
        X_test
    )

    mae = mean_absolute_error(
        y_test,
        predictions
    )

    rmse = mean_squared_error(
        y_test,
        predictions
    ) ** 0.5

    r2 = r2_score(
        y_test,
        predictions
    )

    print(f"MAE  : {mae:.2f} minutes")
    print(f"RMSE : {rmse:.2f} minutes")
    print(f"R²   : {r2:.4f}")

    return {
        "model": model_name,
        "MAE": mae,
        "RMSE": rmse,
        "R2": r2,
    }


# ============================================================
# 9. MODÈLES
# ============================================================

results = []


# ------------------------------------------------------------
# Baseline
# ------------------------------------------------------------

baseline = Pipeline(
    steps=[
        (
            "preprocessor",
            preprocessor,
        ),
        (
            "model",
            DummyRegressor(
                strategy="mean"
            ),
        ),
    ]
)

results.append(
    evaluate_model(
        "Baseline",
        baseline,
    )
)


# ------------------------------------------------------------
# Random Forest
# ------------------------------------------------------------

random_forest = Pipeline(
    steps=[
        (
            "preprocessor",
            preprocessor,
        ),
        (
            "model",
            RandomForestRegressor(
                n_estimators=100,
                max_depth=20,
                random_state=42,
                n_jobs=-1,
            ),
        ),
    ]
)

results.append(
    evaluate_model(
        "Random Forest",
        random_forest,
    )
)


# ------------------------------------------------------------
# Gradient Boosting
# ------------------------------------------------------------

gradient_boosting = Pipeline(
    steps=[
        (
            "preprocessor",
            preprocessor,
        ),
        (
            "model",
            GradientBoostingRegressor(
                n_estimators=100,
                learning_rate=0.05,
                max_depth=5,
                random_state=42,
            ),
        ),
    ]
)

results.append(
    evaluate_model(
        "Gradient Boosting",
        gradient_boosting,
    )
)


# ============================================================
# 10. COMPARAISON DES MODÈLES
# ============================================================

results_df = pd.DataFrame(
    results
)

results_df = results_df.sort_values(
    "MAE"
)


print("\n" + "=" * 60)
print("COMPARAISON DES MODÈLES")
print("=" * 60)

print(
    results_df.to_string(
        index=False
    )
)


# ============================================================
# 11. SAUVEGARDE DES RÉSULTATS
# ============================================================

OUTPUT_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "model_results.csv"
)

results_df.to_csv(
    OUTPUT_PATH,
    index=False
)


print("\nRésultats sauvegardés dans :")
print(OUTPUT_PATH)


print("\n" + "=" * 60)
print("ENTRAÎNEMENT TERMINÉ")
print("=" * 60)