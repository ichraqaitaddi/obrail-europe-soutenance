# Importer les fonctions d'extraction des données
from app.etl.extract import (
    extract_agencies,
    extract_routes,
    extract_trips,
    extract_stops,
    extract_city_from_coordinates_cached
)

# Importer les fonctions de transformation
from app.etl.transform import (
    transform_agencies,
    transform_routes,
    transform_trips,
    transform_stations,
    transform_stops
)

# Importer les fonctions de chargement dans PostgreSQL
from app.etl.load import (
    load_operators,
    load_routes,
    load_trips,
    load_stations,
    load_stops,
    load_city,
    update_station_city
)

# Importer la connexion à PostgreSQL
from app.database.database import SessionLocal

# Importer le modèle Station
from app.models.station import Station


# Limiter le nombre de stations traitées par exécution
# afin de réduire le risque de dépasser la limite GeoNames
MAX_STATIONS_PER_RUN = 400


def run_pipeline():

    # ---------------------------------------------------------
    # 1. OPERATEURS
    # ---------------------------------------------------------

    # Extraire les agences depuis agency.txt
    agencies_df = extract_agencies()

    # Transformer les agences en opérateurs
    operators_df = transform_agencies(agencies_df)

    # Charger les opérateurs dans PostgreSQL
    load_operators(operators_df)


    # ---------------------------------------------------------
    # 2. ROUTES
    # ---------------------------------------------------------

    # Extraire les routes depuis routes.txt
    routes_df = extract_routes()

    # Transformer les routes
    routes_df = transform_routes(routes_df)

    # Charger les routes dans PostgreSQL
    load_routes(routes_df)


    # ---------------------------------------------------------
    # 3. TRIPS
    # ---------------------------------------------------------

    # Extraire les trajets depuis trips.txt
    trips_df = extract_trips()

    # Transformer les trajets
    trips_df = transform_trips(trips_df)

    # Charger les trajets dans PostgreSQL
    load_trips(trips_df)


    # ---------------------------------------------------------
    # 4. STATIONS ET POINTS D'ARRET
    # ---------------------------------------------------------

    # Extraire le fichier stops.txt
    stops_df = extract_stops()

    # Transformer les stations
    stations_df = transform_stations(stops_df)

    # Afficher le nombre total de stations
    print(
        "Nombre de stations :",
        len(stations_df)
    )

    # Charger les stations dans PostgreSQL
    load_stations(stations_df)

    print(
        "Stations chargées dans PostgreSQL avec succès."
    )

    # Transformer les points d'arrêt
    stops_transformed_df = transform_stops(stops_df)

    # Afficher le nombre total de points d'arrêt
    print(
        "Nombre de points d'arrêt :",
        len(stops_transformed_df)
    )

    # Charger les points d'arrêt dans PostgreSQL
    load_stops(stops_transformed_df)

    print(
        "Points d'arrêt chargés dans PostgreSQL avec succès."
    )


    # ---------------------------------------------------------
    # 5. RECUPERER LES STATIONS SANS VILLE
    # ---------------------------------------------------------

    # Ouvrir une connexion à PostgreSQL
    db = SessionLocal()

    # Récupérer uniquement les stations
    # qui n'ont pas encore de ville
    stations_without_city = db.query(Station).filter(
        Station.city_id.is_(None)
    ).all()

    # Fermer la connexion
    db.close()

    # Afficher le nombre de stations restantes
    print(
        "\nStations sans ville :",
        len(stations_without_city)
    )

    # Vérifier s'il reste des stations à traiter
    if not stations_without_city:

        # Toutes les stations sont déjà associées
        print(
            "Toutes les stations ont déjà une ville."
        )

        # Arrêter le pipeline
        return


    # ---------------------------------------------------------
    # 6. LIMITER LE LOT
    # ---------------------------------------------------------

    # Sélectionner uniquement les stations du lot actuel
    stations_to_process = stations_without_city[
        :MAX_STATIONS_PER_RUN
    ]

    # Afficher le nombre de stations du lot
    print(
        "Stations traitées cette fois :",
        len(stations_to_process)
    )


    # ---------------------------------------------------------
    # 7. GEO NAMES
    # ---------------------------------------------------------

    # Afficher le début du traitement GeoNames
    print(
        "\n===== GEO NAMES ====="
    )

    # Parcourir les stations du lot
    for index, station in enumerate(
        stations_to_process,
        start=1
    ):

        # Récupérer les coordonnées de la station
        latitude = station.latitude
        longitude = station.longitude

        # Récupérer l'identifiant GTFS de la station
        station_gtfs_id = station.gtfs_stop_id

        # Afficher la progression
        print(
            f"\nStation {index}/{len(stations_to_process)} : "
            f"{station.name}"
        )

        # Rechercher la ville avec GeoNames
        city_data = extract_city_from_coordinates_cached(
            latitude,
            longitude
        )


        # -----------------------------------------------------
        # 7.1 VERIFIER LA LIMITE GEONAMES
        # -----------------------------------------------------

        # Vérifier si GeoNames a atteint sa limite horaire
        if (
            city_data
            and city_data.get("_error") == "HOURLY_LIMIT"
        ):

            # Afficher un message explicite
            print(
                "\n===== LIMITE GEONAMES ATTEINTE ====="
            )

            print(
                "Le pipeline s'arrête pour cette exécution."
            )

            print(
                "Les stations restantes seront traitées "
                "lors d'une prochaine exécution."
            )

            # Arrêter immédiatement la boucle
            break


        # -----------------------------------------------------
        # 7.2 AUCUNE VILLE TROUVEE
        # -----------------------------------------------------

        # Vérifier si aucune ville n'a été trouvée
        if city_data is None:

            # Afficher qu'aucune ville n'a été trouvée
            print(
                "Aucune ville trouvée par GeoNames."
            )

            # Passer à la station suivante
            continue


        # -----------------------------------------------------
        # 8. ENREGISTRER LA VILLE
        # -----------------------------------------------------

        # Afficher la ville trouvée
        print(
            f"Ville trouvée : "
            f"{city_data['name']} "
            f"({city_data['country_code']})"
        )

        # Charger la ville dans PostgreSQL
        # ou récupérer son identifiant si elle existe déjà
        city_id = load_city(city_data)

        # Associer la station à la ville
        success = update_station_city(
            station_gtfs_id,
            city_id
        )

        # Vérifier si l'association a réussi
        if success:

            # Afficher la confirmation
            print(
                "Station associée à la ville avec succès."
            )

        else:

            # Afficher l'erreur
            print(
                "Erreur lors de l'association "
                "station/ville."
            )


    # ---------------------------------------------------------
    # 9. CALCUL DU NOMBRE REEL DE STATIONS RESTANTES
    # ---------------------------------------------------------

    # Ouvrir une nouvelle connexion à PostgreSQL
    db = SessionLocal()

    # Compter directement dans PostgreSQL
    # les stations qui n'ont toujours pas de ville
    remaining = db.query(Station).filter(
        Station.city_id.is_(None)
    ).count()

    # Fermer la connexion
    db.close()


    # ---------------------------------------------------------
    # 10. FIN DU LOT
    # ---------------------------------------------------------

    # Afficher la fin du traitement
    print(
        "\n===== GEO NAMES TERMINE ====="
    )

    # Afficher le nombre réel restant
    print(
        "Stations encore sans ville :",
        remaining
    )


# ---------------------------------------------------------
# LANCEMENT DU PIPELINE
# ---------------------------------------------------------

# Exécuter le pipeline uniquement lorsque
# le fichier est lancé directement
if __name__ == "__main__":
    run_pipeline()