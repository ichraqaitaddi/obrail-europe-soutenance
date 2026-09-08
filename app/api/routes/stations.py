from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

# Import de la connexion à la base de données
from app.database.database import SessionLocal

# Import du modèle Station
from app.models.station import Station
# Import du modèle City
from app.models.city import City

# Création du routeur dédié aux stations
router = APIRouter(
    prefix="/stations",
    tags=["Stations"]
)


# Fonction permettant d'obtenir une session PostgreSQL
def get_db():
    # Ouvre une connexion à la base de données
    db = SessionLocal()

    try:
        # Donne la connexion à l'endpoint
        yield db

    finally:
        # Ferme la connexion après la requête
        db.close()


# Endpoint GET /stations
# Il récupère toutes les stations enregistrées dans PostgreSQL.
#@router.get("/")
#def get_stations(db: Session = Depends(get_db)):
    # Interroger la table stations
    #stations = db.query(Station).all()

    # Retourner les stations sous forme de liste JSON
    # return stations

# Endpoint GET /stations/
# Permet de récupérer les stations avec une limite
# et éventuellement de filtrer par ville.
@router.get("/")
def get_stations(
    limit: int = 10,
    city_id: int | None = None,
    db: Session = Depends(get_db)
):
    # Commencer la requête sur la table stations
    query = db.query(Station)

    # Si un city_id est fourni,
    # filtrer les stations appartenant à cette ville.
    if city_id is not None:
        query = query.filter(
            Station.city_id == city_id
        )

    # Limiter le nombre de résultats retournés
    stations = query.limit(limit).all()

    # Retourner les stations sous forme de liste JSON
    return stations



# Endpoint GET /stations/{station_id}
# Il permet de récupérer une seule station grâce à son identifiant.
@router.get("/{station_id}")
def get_station(
    station_id: int,
    db: Session = Depends(get_db)
):
    # Rechercher la station correspondant à l'identifiant demandé
    station = db.query(Station).filter(
        Station.id == station_id
    ).first()

    # Si aucune station n'est trouvée,
    # retourner une erreur HTTP 404.
    if station is None:
        raise HTTPException(
            status_code=404,
            detail="Station introuvable"
        )

    # Retourner les informations de la station
    return station

# Endpoint GET /stations/{station_id}/city
# Il permet de récupérer la ville associée à une station.
@router.get("/{station_id}/city")
def get_station_city(
    station_id: int,
    db: Session = Depends(get_db)
):
    # Rechercher la station avec son identifiant
    station = db.query(Station).filter(
        Station.id == station_id
    ).first()

    # Vérifier que la station existe
    if station is None:
        raise HTTPException(
            status_code=404,
            detail="Station introuvable"
        )

    # Vérifier que la station possède une ville
    if station.city_id is None:
        raise HTTPException(
            status_code=404,
            detail="Aucune ville associée à cette station"
        )

    # Rechercher la ville associée dans la table cities
    city = db.query(City).filter(
        City.id == station.city_id
    ).first()

    # Vérifier que la ville existe réellement
    if city is None:
        raise HTTPException(
            status_code=404,
            detail="Ville introuvable"
        )

    # Retourner les informations de la ville
    return city


