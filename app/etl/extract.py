# Importer Path pour construire les chemins de fichiers
from pathlib import Path

# Importer Pandas pour lire et manipuler les fichiers de données
import pandas as pd

# Importer requests pour envoyer des requêtes HTTP vers GeoNames
import requests

# Importer la fonction qui transforme la hiérarchie GeoNames
from app.etl.transform import transform_geonames_hierarchy


# =========================================================
# CONFIGURATION DES CHEMINS
# =========================================================

# Trouver le dossier principal du projet
BASE_DIR = Path(__file__).resolve().parents[2]

# Construire le chemin vers le dossier des données brutes
RAW_DATA_DIR = BASE_DIR / "data" / "raw"


# =========================================================
# EXTRACTION DES AGENCES
# =========================================================

def extract_agencies():
    # Chercher le fichier agency.txt dans raw et ses sous-dossiers
    agency_files = list(RAW_DATA_DIR.rglob("agency.txt"))

    # Arrêter le programme si aucun fichier n'est trouvé
    if not agency_files:
        raise FileNotFoundError(
            "Impossible de trouver agency.txt"
        )

    # Récupérer le chemin du premier fichier trouvé
    agency_path = agency_files[0]

    # Lire le fichier CSV avec Pandas
    df = pd.read_csv(agency_path)

    # Retourner les données extraites
    return df


# =========================================================
# EXTRACTION DES ROUTES
# =========================================================

def extract_routes():
    # Chercher le fichier routes.txt dans raw et ses sous-dossiers
    route_files = list(RAW_DATA_DIR.rglob("routes.txt"))

    # Arrêter le programme si aucun fichier n'est trouvé
    if not route_files:
        raise FileNotFoundError(
            "Impossible de trouver routes.txt"
        )

    # Récupérer le chemin du premier fichier trouvé
    route_path = route_files[0]

    # Lire le fichier CSV avec Pandas
    df = pd.read_csv(route_path)

    # Retourner les données extraites
    return df


# =========================================================
# EXTRACTION DES TRIPS
# =========================================================

def extract_trips():
    # Chercher le fichier trips.txt dans raw et ses sous-dossiers
    trip_files = list(RAW_DATA_DIR.rglob("trips.txt"))

    # Arrêter le programme si aucun fichier n'est trouvé
    if not trip_files:
        raise FileNotFoundError(
            "Impossible de trouver trips.txt"
        )

    # Récupérer le chemin du premier fichier trouvé
    trip_path = trip_files[0]

    # Lire le fichier CSV avec Pandas
    df = pd.read_csv(trip_path)

    # Retourner les données extraites
    return df


# =========================================================
# EXTRACTION DES STATIONS ET POINTS D'ARRET
# =========================================================

def extract_stops():
    # Rechercher le fichier stops.txt dans tous les sous-dossiers
    stop_files = list(RAW_DATA_DIR.rglob("stops.txt"))

    # Vérifier que le fichier existe
    if not stop_files:
        raise FileNotFoundError(
            "Impossible de trouver stops.txt"
        )

    # Récupérer le premier fichier trouvé
    stop_path = stop_files[0]

    # Lire le fichier GTFS avec Pandas
    df = pd.read_csv(stop_path)

    # Retourner les données extraites
    return df


# =========================================================
# GEO NAMES : RECHERCHE D'UN LIEU
# =========================================================

def extract_geonames(latitude: float, longitude: float):
    # Construire l'URL du service GeoNames
    url = "http://api.geonames.org/findNearbyPlaceNameJSON"

    # Préparer les paramètres envoyés à GeoNames
    params = {
        "lat": latitude,
        "lng": longitude,
        "username": "ichraq.aitaddi"
    }

    try:
        # Envoyer la requête à GeoNames
        # Le timeout évite que le pipeline reste bloqué trop longtemps
        response = requests.get(
            url,
            params=params,
            timeout=10
        )

        # Vérifier les erreurs HTTP éventuelles
        response.raise_for_status()

        # Transformer la réponse JSON en dictionnaire Python
        data = response.json()

        # Vérifier si GeoNames a retourné une erreur
        # directement dans le contenu JSON
        if "status" in data:

            # Récupérer le message d'erreur retourné par GeoNames
            message = data["status"].get("message", "")

            # Vérifier si la limite horaire a été dépassée
            if "hourly limit" in message.lower():

                # Afficher clairement que la limite a été atteinte
                print(
                    "LIMITE GEONAMES ATTEINTE : "
                    f"{message}"
                )

                # Retourner un résultat spécial permettant
                # au reste du pipeline de reconnaître cette situation
                return {
                    "geonames": [],
                    "_error": "HOURLY_LIMIT"
                }

            # Afficher les autres erreurs GeoNames
            print(
                f"Erreur GeoNames : {message}"
            )

            # Retourner un résultat vide pour les autres erreurs
            return {
                "geonames": []
            }

        # Retourner les données GeoNames normales
        return data

    except requests.exceptions.Timeout:
        # Gérer le cas où GeoNames met trop de temps à répondre
        print(
            f"GeoNames a dépassé le délai pour "
            f"les coordonnées ({latitude}, {longitude})."
        )

        # Retourner None en cas de timeout
        return None

    except requests.exceptions.RequestException as error:
        # Gérer les autres erreurs liées à la requête HTTP
        print(
            f"Erreur réseau GeoNames pour "
            f"les coordonnées ({latitude}, {longitude}) : {error}"
        )

        # Retourner None en cas d'erreur réseau
        return None


# =========================================================
# GEO NAMES : HIERARCHIE D'UN LIEU
# =========================================================

def extract_geonames_hierarchy(geoname_id: int):
    # Construire l'URL du service hierarchy de GeoNames
    url = "http://api.geonames.org/hierarchyJSON"

    # Préparer les paramètres envoyés à GeoNames
    params = {
        "geonameId": geoname_id,
        "username": "ichraq.aitaddi"
    }

    try:
        # Envoyer la requête à GeoNames
        # avec un délai maximum de 10 secondes
        response = requests.get(
            url,
            params=params,
            timeout=10
        )

        # Déclencher une erreur si GeoNames
        # retourne une erreur HTTP
        response.raise_for_status()

        # Transformer la réponse JSON
        # en dictionnaire Python
        data = response.json()

        # Retourner les données reçues
        return data

    except requests.exceptions.Timeout:
        # Gérer le cas où GeoNames met trop de temps à répondre
        print(
            f"GeoNames hierarchy a dépassé le délai "
            f"pour l'identifiant {geoname_id}."
        )

        # Retourner une hiérarchie vide
        return {
            "geonames": []
        }

    except requests.exceptions.RequestException as error:
        # Gérer les autres erreurs liées à la requête HTTP
        print(
            f"Erreur GeoNames hierarchy pour "
            f"l'identifiant {geoname_id} : {error}"
        )

        # Retourner une hiérarchie vide
        return {
            "geonames": []
        }


# =========================================================
# GEO NAMES : RECUPERER LA VILLE D'UNE STATION
# =========================================================

def extract_city_from_coordinates(
    latitude: float,
    longitude: float
):
    # Appeler GeoNames pour trouver le lieu le plus proche
    nearby_data = extract_geonames(
        latitude,
        longitude
    )

    # Vérifier si GeoNames a atteint sa limite horaire
    if nearby_data and nearby_data.get("_error") == "HOURLY_LIMIT":

        # Retourner le même signal d'erreur
        # pour que le pipeline puisse arrêter le traitement
        return {
            "_error": "HOURLY_LIMIT"
        }

    # Vérifier si aucune réponse n'a été reçue
    if nearby_data is None:
        return None

    # Récupérer les lieux retournés par GeoNames
    geonames = nearby_data.get(
        "geonames",
        []
    )

    # Si aucun lieu n'est trouvé, retourner None
    if not geonames:
        return None

    # Récupérer le premier lieu retourné par GeoNames
    nearest_place = geonames[0]

    # Récupérer son identifiant GeoNames
    geoname_id = nearest_place.get(
        "geonameId"
    )

    # Vérifier que l'identifiant existe
    if geoname_id is None:
        return None

    # Récupérer la hiérarchie complète de ce lieu
    hierarchy_data = extract_geonames_hierarchy(
        geoname_id
    )

    # Transformer la hiérarchie pour obtenir
    # la ville et le pays
    city = transform_geonames_hierarchy(
        hierarchy_data
    )

    # Retourner les informations de la ville
    return city


# =========================================================
# CACHE GEO NAMES
# =========================================================

# Cache pour éviter de refaire plusieurs fois
# la même recherche GeoNames
_geonames_city_cache = {}


def extract_city_from_coordinates_cached(
    latitude: float,
    longitude: float
):
    # Créer une clé unique à partir des coordonnées
    coordinates_key = (
        latitude,
        longitude
    )

    # Vérifier si ces coordonnées ont déjà été traitées
    if coordinates_key in _geonames_city_cache:

        # Retourner directement le résultat
        # déjà obtenu précédemment
        return _geonames_city_cache[
            coordinates_key
        ]

    # Appeler GeoNames si les coordonnées
    # ne sont pas encore présentes dans le cache
    city = extract_city_from_coordinates(
        latitude,
        longitude
    )

    # Enregistrer le résultat dans le cache
    _geonames_city_cache[
        coordinates_key
    ] = city

    # Retourner la ville trouvée
    return city