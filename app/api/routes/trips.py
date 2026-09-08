from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

# Import de la connexion à la base de données
from app.database.database import SessionLocal

# Import du modèle Trip
from app.models.trip import Trip


# Création du routeur dédié aux trajets
router = APIRouter(
    prefix="/trips",
    tags=["Trips"]
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


# Endpoint GET /trips/
# Permet de récupérer les trips avec une limite
# et éventuellement de filtrer par route.
@router.get("/")
def get_trips(
    limit: int = 10,
    route_id: int | None = None,
    db: Session = Depends(get_db)
):
    # Commencer la requête sur la table trips
    query = db.query(Trip)

    # Si un route_id est fourni,
    # filtrer les trips appartenant à cette route.
    if route_id is not None:
        query = query.filter(
            Trip.route_id == route_id
        )

    # Limiter le nombre de résultats retournés
    trips = query.limit(limit).all()

    # Retourner les trips sous forme de liste JSON
    return trips