from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


# ============================================================
# 1. CHEMINS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_PATH = BASE_DIR / "data" / "processed" / "dataset_ml.csv"
MODEL_DIR = BASE_DIR / "models_ml"
MODEL_PATH = MODEL_DIR / "random_forest.pkl"

MODEL_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# 2. CHARGEMENT DU DATASET
# ============================================================

print("Chargement du dataset...")

df = pd.read_csv(DATA_PATH)

print(f"Dataset : {df.shape[0]} lignes, {df.shape[1]} colonnes")


# ============================================================
# 3. EXTRACTION DE LA DATE
# ============================================================

# La date de service est présente dans le trip_id.
# Elle sert uniquement à créer un split temporel.
df["service_date"] = pd.to_datetime(
    df["trip_id"].str.extract(r"(20\d{6})")[0],
    format="%Y%m%d"
)

print(
    f"Période : {df['service_date'].min().date()} "
    f"→ {df['service_date'].max().date()}"
)


# ============================================================
# 4. FEATURES ET TARGET
# ============================================================

target = "duration_minutes"

features = [
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

X = df[features]
y = df[target]


# ============================================================
# 5. SPLIT TEMPOREL
# ============================================================

unique_dates = sorted(df["service_date"].unique())

cutoff_index = int(len(unique_dates) * 0.80)
cutoff_date = unique_dates[cutoff_index]

train_mask = df["service_date"] < cutoff_date
test_mask = df["service_date"] >= cutoff_date

X_train = X.loc[train_mask]
X_test = X.loc[test_mask]

y_train = y.loc[train_mask]
y_test = y.loc[test_mask]

print("\n--- SPLIT TEMPOREL ---")
print(f"Date de coupure : {pd.Timestamp(cutoff_date).date()}")

print(f"Train : {len(X_train)} lignes")
print(
    f"Dates train : "
    f"{df.loc[train_mask, 'service_date'].min().date()} "
    f"→ {df.loc[train_mask, 'service_date'].max().date()}"
)

print(f"Test : {len(X_test)} lignes")
print(
    f"Dates test : "
    f"{df.loc[test_mask, 'service_date'].min().date()} "
    f"→ {df.loc[test_mask, 'service_date'].max().date()}"
)


# ============================================================
# 6. PREPROCESSING
# ============================================================

categorical_features = [
    "route_id",
    "agency_id",
    "route_type",
    "direction_id",
    "origin_stop_id",
    "destination_stop_id",
]

numeric_features = [
    "n_stops",
    "departure_hour",
    "departure_minute",
    "distance_km",
]

preprocessor = ColumnTransformer(
    transformers=[
        (
            "categorical",
            OneHotEncoder(handle_unknown="ignore"),
            categorical_features,
        ),
        (
            "numeric",
            "passthrough",
            numeric_features,
        ),
    ]
)


# ============================================================
# 7. RANDOM FOREST
# ============================================================

model = RandomForestRegressor(
    n_estimators=100,
    max_depth=20,
    random_state=42,
    n_jobs=-1,
)


pipeline = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        ("model", model),
    ]
)


# ============================================================
# 8. ENTRAINEMENT
# ============================================================

print("\nEntraînement du Random Forest...")

pipeline.fit(X_train, y_train)

print("Entraînement terminé.")


# ============================================================
# 9. PRÉDICTIONS
# ============================================================

y_pred = pipeline.predict(X_test)


# ============================================================
# 10. MÉTRIQUES
# ============================================================

mae = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
r2 = r2_score(y_test, y_pred)

print("\n========== ÉVALUATION RANDOM FOREST ==========")

print(f"MAE  : {mae:.2f} minutes")
print(f"RMSE : {rmse:.2f} minutes")
print(f"R²   : {r2:.4f}")


# ============================================================
# 11. ANALYSE DES ERREURS
# ============================================================

errors = y_pred - y_test.to_numpy()
absolute_errors = np.abs(errors)

print("\n========== ANALYSE DES ERREURS ==========")

print(f"Erreur moyenne absolue : {absolute_errors.mean():.2f} min")
print(f"Erreur maximale        : {absolute_errors.max():.2f} min")

for threshold in [5, 10, 15, 30]:
    percentage = (absolute_errors <= threshold).mean() * 100
    print(
        f"Prédictions avec erreur ≤ {threshold:2d} min : "
        f"{percentage:.2f}%"
    )


# ============================================================
# 12. FEATURES IMPORTANTES
# ============================================================

print("\n========== FEATURES IMPORTANTES ==========")

trained_preprocessor = pipeline.named_steps["preprocessor"]
trained_model = pipeline.named_steps["model"]

feature_names = trained_preprocessor.get_feature_names_out()
importances = trained_model.feature_importances_

importance_df = pd.DataFrame({
    "feature": feature_names,
    "importance": importances,
})

importance_df = importance_df.sort_values(
    "importance",
    ascending=False
)

print("\nTop 20 features :")
print(importance_df.head(20).to_string(index=False))


# ============================================================
# 13. AGRÉGATION PAR FEATURE ORIGINALE
# ============================================================

def get_original_feature(feature_name):
    """
    Transforme par exemple :
    categorical__route_id_FR:Line::xxx
    en :
    route_id
    """

    feature_name = feature_name.replace(
        "categorical__", ""
    ).replace(
        "numeric__", ""
    )

    for feature in features:
        if feature_name == feature or feature_name.startswith(
            feature + "_"
        ):
            return feature

    return feature_name


importance_df["original_feature"] = (
    importance_df["feature"]
    .apply(get_original_feature)
)

aggregated_importance = (
    importance_df
    .groupby("original_feature")["importance"]
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)

print("\nImportance par variable originale :")
print(
    aggregated_importance.to_string(index=False)
)


# ============================================================
# 14. SAUVEGARDE DES PRÉDICTIONS
# ============================================================

predictions = X_test.copy()

predictions["actual_duration_minutes"] = y_test.to_numpy()
predictions["predicted_duration_minutes"] = y_pred
predictions["absolute_error_minutes"] = absolute_errors

predictions_path = (
    BASE_DIR
    / "data"
    / "processed"
    / "predictions_random_forest.csv"
)

predictions.to_csv(
    predictions_path,
    index=False
)


# ============================================================
# 15. SAUVEGARDE DES IMPORTANCES
# ============================================================

importance_path = (
    BASE_DIR
    / "data"
    / "processed"
    / "feature_importance.csv"
)

aggregated_importance.to_csv(
    importance_path,
    index=False
)


# ============================================================
# 16. SAUVEGARDE DU MODÈLE
# ============================================================

joblib.dump(
    pipeline,
    MODEL_PATH
)

print("\n========== FICHIERS SAUVEGARDÉS ==========")

print(f"Modèle : {MODEL_PATH}")
print(f"Prédictions : {predictions_path}")
print(f"Features importantes : {importance_path}")

print("\nÉvaluation terminée.")