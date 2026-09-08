# Importer Pandas pour manipuler les données sous forme de DataFrame
import pandas as pd


# ============================================================
# TRANSFORMATION DES AGENCES
# ============================================================

def transform_agencies(df: pd.DataFrame):
    # Garder uniquement les colonnes utiles
    operators_df = df[
        ["agency_id", "agency_name", "agency_url"]
    ].copy()

    # Renommer les colonnes pour correspondre à notre table operators
    operators_df = operators_df.rename(
        columns={
            "agency_id": "gtfs_agency_id",
            "agency_name": "name",
            "agency_url": "website"
        }
    )

    # Retourner les données transformées
    return operators_df


# ============================================================
# TRANSFORMATION DES ROUTES
# ============================================================

def transform_routes(df: pd.DataFrame):
    # Garder uniquement les colonnes utiles pour notre table routes
    routes_df = df[
        [
            "route_id",
            "agency_id",
            "route_short_name",
            "route_long_name"
        ]
    ].copy()

    # Renommer les colonnes pour correspondre à notre modèle Route
    routes_df = routes_df.rename(
        columns={
            "route_id": "gtfs_route_id",
            "route_short_name": "short_name",
            "route_long_name": "long_name"
        }
    )

    # Retourner les données transformées
    return routes_df


# ============================================================
# TRANSFORMATION DES TRAINS / TRIPS
# ============================================================

def transform_trips(df: pd.DataFrame):

    # Garder uniquement les colonnes utiles
    trips_df = df[
        [
            "trip_id",
            "route_id",
            "service_id",
            "trip_headsign",
            "direction_id"
        ]
    ].copy()

    # Renommer les colonnes pour correspondre à notre modèle Trip
    trips_df = trips_df.rename(
        columns={
            "trip_id": "gtfs_trip_id",
            "trip_headsign": "headsign"
        }
    )

    # Transformer les valeurs de direction_id en valeurs numériques
    # Les valeurs impossibles à convertir deviennent NaN
    trips_df["direction_id"] = (
        pd.to_numeric(
            trips_df["direction_id"],
            errors="coerce"
        )
        .astype("Int64")
    )

    # Convertir les valeurs manquantes Pandas en None
    trips_df["direction_id"] = trips_df["direction_id"].where(
        trips_df["direction_id"].notna(),
        None
    )

    # Convertir service_id et headsign en chaînes de caractères
    trips_df["service_id"] = trips_df["service_id"].astype(str)
    trips_df["headsign"] = trips_df["headsign"].astype(str)

    # Retourner les données transformées
    return trips_df


# ============================================================
# TRANSFORMATION DES STATIONS
# ============================================================

def transform_stations(df: pd.DataFrame):

    # Garder uniquement les lignes qui représentent une station principale
    # Dans le format GTFS, location_type = 1 correspond à une station
    stations_df = df[
        df["location_type"] == 1
    ].copy()

    # Sélectionner uniquement les colonnes nécessaires
    stations_df = stations_df[
        [
            "stop_id",
            "stop_name",
            "stop_lat",
            "stop_lon"
        ]
    ].copy()

    # Renommer les colonnes GTFS pour correspondre à notre modèle Station
    stations_df = stations_df.rename(
        columns={
            "stop_id": "gtfs_stop_id",
            "stop_name": "name",
            "stop_lat": "latitude",
            "stop_lon": "longitude"
        }
    )

    # Retourner les données transformées
    return stations_df


# ============================================================
# TRANSFORMATION DES POINTS D'ARRÊT
# ============================================================

def transform_stops(df: pd.DataFrame):

    # Garder uniquement les lignes qui représentent des points d'arrêt
    # Dans le format GTFS, location_type = 0 correspond à un point d'arrêt
    stops_df = df[
        df["location_type"] == 0
    ].copy()

    # Sélectionner uniquement les colonnes nécessaires
    stops_df = stops_df[
        [
            "stop_id",
            "stop_name",
            "parent_station"
        ]
    ].copy()

    # Renommer les colonnes pour correspondre à notre modèle Stop
    stops_df = stops_df.rename(
        columns={
            "stop_id": "gtfs_stop_id",
            "stop_name": "name",
            "parent_station": "gtfs_station_id"
        }
    )

    # Retourner les données transformées
    return stops_df


# ============================================================
# TRANSFORMATION DES DONNÉES GEONAMES
# ============================================================

def transform_geonames_hierarchy(data):

    # Vérifier que les données reçues sont bien un dictionnaire
    if not data:
        return None

    # Récupérer la liste des lieux présents dans la hiérarchie
    geonames = data.get("geonames", [])

    # Si aucun lieu n'est présent, retourner None
    if not geonames:
        return None

    # --------------------------------------------------------
    # 1. PRIORITÉ AUX COMMUNES / VILLES ADM4
    # --------------------------------------------------------
    #
    # ADM4 correspond généralement à une commune.
    # C'est donc notre premier choix lorsqu'elle est disponible.
    for place in geonames:

        # Vérifier si le lieu est une division administrative ADM4
        if place.get("fcode") == "ADM4":

            # Récupérer le nom de la commune
            name = place.get("name")

            # Récupérer l'identifiant GeoNames
            geoname_id = place.get("geonameId")

            # Vérifier que les informations essentielles existent
            if name and geoname_id:

                # Retourner les informations de la commune
                return {
                    "geonames_id": geoname_id,
                    "name": name,
                    "country_code": place.get("countryCode")
                }

    # --------------------------------------------------------
    # 2. SI ADM4 ABSENTE : CHERCHER UN LIEU PEUPLÉ
    # --------------------------------------------------------
    #
    # PPL peut correspondre à une ville, un village ou une localité.
    # On l'utilise donc comme deuxième possibilité.
    for place in geonames:

        # Vérifier si le lieu appartient à la classe P
        if place.get("fcl") == "P":

            # Récupérer le nom du lieu
            name = place.get("name")

            # Récupérer l'identifiant GeoNames
            geoname_id = place.get("geonameId")

            # Vérifier que les informations essentielles existent
            if name and geoname_id:

                # Retourner le lieu peuplé
                return {
                    "geonames_id": geoname_id,
                    "name": name,
                    "country_code": place.get("countryCode")
                }

    # --------------------------------------------------------
    # 3. ADM3 COMME SOLUTION DE SECOURS
    # --------------------------------------------------------
    #
    # ADM3 peut correspondre à un arrondissement.
    # On ne l'utilise donc qu'en dernier recours.
    for place in geonames:

        # Vérifier si le lieu est une division administrative ADM3
        if place.get("fcode") == "ADM3":

            # Récupérer le nom
            name = place.get("name")

            # Récupérer l'identifiant GeoNames
            geoname_id = place.get("geonameId")

            # Vérifier que les informations essentielles existent
            if name and geoname_id:

                # Nettoyer certains noms administratifs allemands
                name = name.replace(
                    "Kreisfreie Stadt ",
                    ""
                )

                name = name.replace(
                    "Stadtkreis ",
                    ""
                )

                name = name.replace(
                    ", Stadt",
                    ""
                )

                # Ne pas utiliser explicitement un arrondissement
                # comme ville
                if (
                    "Arrondissement" in name
                    or "arrondissement" in name
                ):
                    continue

                # Retourner les informations trouvées
                return {
                    "geonames_id": geoname_id,
                    "name": name,
                    "country_code": place.get("countryCode")
                }

    # --------------------------------------------------------
    # 4. ADM2 N'EST PAS UTILISÉE
    # --------------------------------------------------------
    #
    # ADM2 peut correspondre à un département ou une autre
    # division administrative.
    #
    # Exemple :
    # "Indre-et-Loire" n'est pas la ville de la station.

    # --------------------------------------------------------
    # 5. AUCUNE VILLE EXPLOITABLE
    # --------------------------------------------------------

    return None


# ============================================================
# COORDONNÉES UNIQUES DES STATIONS
# ============================================================

def transform_unique_station_coordinates(df: pd.DataFrame):

    # Garder uniquement les stations principales
    # location_type = 1
    stations_df = df[
        df["location_type"] == 1
    ].copy()

    # Garder uniquement les colonnes nécessaires
    coordinates_df = stations_df[
        [
            "stop_id",
            "stop_lat",
            "stop_lon"
        ]
    ].copy()

    # Supprimer les éventuelles coordonnées identiques
    coordinates_df = coordinates_df.drop_duplicates(
        subset=[
            "stop_lat",
            "stop_lon"
        ]
    )

    # Renommer les colonnes pour les rendre plus explicites
    coordinates_df = coordinates_df.rename(
        columns={
            "stop_id": "gtfs_station_id",
            "stop_lat": "latitude",
            "stop_lon": "longitude"
        }
    )

    # Réinitialiser les index après la suppression des doublons
    coordinates_df = coordinates_df.reset_index(
        drop=True
    )

    # Retourner les coordonnées uniques
    return coordinates_df