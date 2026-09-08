from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

# Import de la connexion à la base de données
from app.database.database import SessionLocal

# Import des modèles
from app.models.route import Route
from app.models.operator import Operator
# Import du modèle Trip
from app.models.trip import Trip
# Création du routeur dédié aux routes ferroviaires
router = APIRouter(
    prefix="/routes",
    tags=["Routes"]
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


# Endpoint GET /routes/
# Il récupère toutes les routes enregistrées dans PostgreSQL.
@router.get("/")
def get_routes(db: Session = Depends(get_db)):
    # Interroger la table routes
    routes = db.query(Route).all()

    # Retourner les routes sous forme de liste JSON
    return routes


# Endpoint GET /routes/{route_id}/operator
# Il permet de récupérer l'opérateur associé à une route.
@router.get("/{route_id}/operator")
def get_route_operator(
    route_id: int,
    db: Session = Depends(get_db)
):
    # Rechercher la route correspondant à l'identifiant demandé
    route = db.query(Route).filter(
        Route.id == route_id
    ).first()

    # Vérifier que la route existe
    if route is None:
        raise HTTPException(
            status_code=404,
            detail="Route introuvable"
        )

    # Vérifier que la route possède un opérateur
    if route.operator_id is None:
        raise HTTPException(
            status_code=404,
            detail="Aucun opérateur associé à cette route"
        )

    # Rechercher l'opérateur associé dans la table operators
    operator = db.query(Operator).filter(
        Operator.id == route.operator_id
    ).first()

    # Vérifier que l'opérateur existe réellement
    if operator is None:
        raise HTTPException(
            status_code=404,
            detail="Opérateur introuvable"
        )

    # Retourner les informations de l'opérateur
    return operator


# Endpoint GET /routes/{route_id}/trips
# Il permet de récupérer les trips appartenant à une route.
@router.get("/{route_id}/trips")
def get_route_trips(
    route_id: int,
    db: Session = Depends(get_db)
):
    # Vérifier que la route existe
    route = db.query(Route).filter(
        Route.id == route_id
    ).first()

    # Si la route n'existe pas, retourner une erreur 404
    if route is None:
        raise HTTPException(
            status_code=404,
            detail="Route introuvable"
        )

    # Rechercher les trips associés à cette route
    trips = db.query(Trip).filter(
        Trip.route_id == route_id
    ).all()

    # Retourner les trips sous forme de liste JSON
    return trips