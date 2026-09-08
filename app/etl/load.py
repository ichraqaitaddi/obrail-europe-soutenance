
import pandas as pd

# Importer la session permettant de communiquer avec PostgreSQL
from app.database.database import SessionLocal

# Importer le modèle Country pour accéder à la table countries
from app.models.country import Country

# Importer le modèle Operator pour ajouter des données dans operators
from app.models.operator import Operator

# Importer le modèle Route pour ajouter des données dans routes
from app.models.route import Route
# Importer le modèle Trip pour ajouter des données dans trips
from app.models.trip import Trip
# Importer le modèle Station pour ajouter les stations dans PostgreSQL
from app.models.station import Station
# Importer le modèle Stop pour ajouter les points d'arrêt dans PostgreSQL
from app.models.stop import Stop
# Importer le modèle City pour gérer les villes dans PostgreSQL
from app.models.city import City




def load_operators(operators_df):

    # Créer une session pour communiquer avec PostgreSQL
    db = SessionLocal()

    # Chercher la France dans la table countries
    country = db.query(Country).filter(
        Country.name == "France"
    ).first()

    # Vérifier que la France existe dans la base de données
    if country is None:
        db.close()
        raise ValueError("Le pays France n'existe pas dans la base de données")

    # Parcourir chaque opérateur du DataFrame
    for _, row in operators_df.iterrows():

        # Vérifier si l'opérateur existe déjà
        existing_operator = db.query(Operator).filter(
            Operator.gtfs_agency_id == row["gtfs_agency_id"]
        ).first()

        # Si l'opérateur existe déjà, on ne l'ajoute pas
        if existing_operator is not None:
            continue

        # Créer un nouvel opérateur
        operator = Operator(
            gtfs_agency_id=row["gtfs_agency_id"],
            name=row["name"],
            website=row["website"],
            country_id=country.id
        )

        # Ajouter l'opérateur à la session
        db.add(operator)

    # Enregistrer les nouveaux opérateurs
    db.commit()

    # Fermer la connexion
    db.close()


# Charger les routes dans PostgreSQL


def load_routes(routes_df):

    # Créer une session pour communiquer avec PostgreSQL
    db = SessionLocal()

    # Parcourir chaque route du DataFrame
    for _, row in routes_df.iterrows():

        # Vérifier si la route existe déjà
        existing_route = db.query(Route).filter(
            Route.gtfs_route_id == row["gtfs_route_id"]
        ).first()

        # Si la route existe déjà, on ne l'ajoute pas
        if existing_route is not None:
            continue

        # Chercher l'opérateur correspondant à l'agency_id GTFS
        operator = db.query(Operator).filter(
            Operator.gtfs_agency_id == row["agency_id"]
        ).first()

        # Vérifier que l'opérateur existe dans la base
        if operator is None:
            continue

        # Créer une nouvelle route
        route = Route(
            gtfs_route_id=row["gtfs_route_id"],
            short_name=row["short_name"],
            long_name=row["long_name"],
            operator_id=operator.id
        )

        # Ajouter la route à la session PostgreSQL
        db.add(route)

    # Enregistrer les nouvelles routes
    db.commit()

    # Fermer la connexion
    db.close()

def load_trips(trips_df):

    # Créer une session pour communiquer avec PostgreSQL
    db = SessionLocal()

    # Parcourir chaque trip du DataFrame
    for _, row in trips_df.iterrows():

        # Vérifier si le trip existe déjà
        existing_trip = db.query(Trip).filter(
            Trip.gtfs_trip_id == row["gtfs_trip_id"]
        ).first()

        # Si le trip existe déjà, on ne l'ajoute pas
        if existing_trip is not None:
            continue

        # Chercher la route correspondant au route_id provenant du GTFS
        route = db.query(Route).filter(
            Route.gtfs_route_id == row["route_id"]
        ).first()

        # Vérifier que la route existe dans la base
        if route is None:
            continue

        # Créer un nouveau trip
        trip = Trip(
            gtfs_trip_id=row["gtfs_trip_id"],
            route_id=route.id,
            service_id=row["service_id"],
            headsign=row["headsign"],
            direction_id=(
                None if pd.isna(row["direction_id"])
                else int(row["direction_id"])
)
        )

        
        # Ajouter le trip à la session PostgreSQL
        db.add(trip)

      
        

       # Enregistrer les nouveaux trips
    db.commit()

    # Fermer la connexion
    db.close()


# Charger les stations dans PostgreSQL
def load_stations(stations_df):

    # Créer une session pour communiquer avec PostgreSQL
    db = SessionLocal()

    # Parcourir chaque station du DataFrame
    for _, row in stations_df.iterrows():

        # Vérifier si la station existe déjà grâce à son identifiant GTFS
        existing_station = db.query(Station).filter(
            Station.gtfs_stop_id == row["gtfs_stop_id"]
        ).first()

        # Si la station existe déjà, ne pas l'ajouter une deuxième fois
        if existing_station is not None:
            continue

        # Créer une nouvelle station
        station = Station(
            gtfs_stop_id=row["gtfs_stop_id"],
            name=row["name"],
            latitude=row["latitude"],
            longitude=row["longitude"]
        )

        # Ajouter la station à la session PostgreSQL
        db.add(station)

    # Enregistrer toutes les nouvelles stations dans PostgreSQL
    db.commit()

    # Fermer la connexion
    db.close()


    # Charger les points d'arrêt dans PostgreSQL
def load_stops(stops_df):

    # Créer une session pour communiquer avec PostgreSQL
    db = SessionLocal()

    # Parcourir chaque point d'arrêt du DataFrame
    for _, row in stops_df.iterrows():

        # Vérifier si le point d'arrêt existe déjà
        existing_stop = db.query(Stop).filter(
            Stop.gtfs_stop_id == row["gtfs_stop_id"]
        ).first()

        # Si le point d'arrêt existe déjà, ne pas l'ajouter une deuxième fois
        if existing_stop is not None:
            continue

        # Chercher la station principale correspondant au parent_station GTFS
        station = db.query(Station).filter(
            Station.gtfs_stop_id == row["gtfs_station_id"]
        ).first()

        # Si aucune station correspondante n'est trouvée, ignorer ce point d'arrêt
        if station is None:
            continue

        # Créer un nouveau point d'arrêt
        stop = Stop(
            gtfs_stop_id=row["gtfs_stop_id"],
            name=row["name"],
            station_id=station.id
        )

        # Ajouter le point d'arrêt à la session PostgreSQL
        db.add(stop)

    # Enregistrer les nouveaux points d'arrêt
    db.commit()

    # Fermer la connexion à la base de données
    db.close()

# Charger une ville dans PostgreSQL et retourner son identifiant interne
def load_city(city_data):
    # Ouvrir une connexion à la base de données
    db = SessionLocal()

    # Vérifier que la ville existe déjà grâce à son identifiant GeoNames
    existing_city = db.query(City).filter(
        City.geonames_id == city_data["geonames_id"]
    ).first()

    # Si la ville existe déjà, récupérer son identifiant interne
    if existing_city is not None:
        city_id = existing_city.id

        # Fermer la connexion
        db.close()

        # Retourner l'identifiant de la ville
        return city_id

    # Créer une nouvelle ville
    city = City(
        geonames_id=city_data["geonames_id"],
        name=city_data["name"],
        country_code=city_data["country_code"]
    )

    # Ajouter la ville à la session SQLAlchemy
    db.add(city)

    # Valider l'insertion dans PostgreSQL
    db.commit()

    # Actualiser l'objet pour récupérer son ID généré par PostgreSQL
    db.refresh(city)

    # Récupérer l'identifiant interne de la ville
    city_id = city.id

    # Fermer la connexion
    db.close()

    # Retourner l'identifiant interne
    return city_id

# Associer une station à une ville dans PostgreSQL
def update_station_city(station_gtfs_id, city_id):
    # Ouvrir une connexion à la base de données
    db = SessionLocal()

    # Rechercher la station grâce à son identifiant GTFS
    station = db.query(Station).filter(
        Station.gtfs_stop_id == station_gtfs_id
    ).first()

    # Vérifier que la station existe
    if station is None:
        db.close()
        return False

    # Affecter l'identifiant interne de la ville à la station
    station.city_id = city_id

    # Enregistrer la modification dans PostgreSQL
    db.commit()

    # Fermer la connexion
    db.close()

    # Indiquer que la mise à jour a réussi
    return True