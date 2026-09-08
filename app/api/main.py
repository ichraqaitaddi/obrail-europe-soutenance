from fastapi import FastAPI

# Importer les modèles pour que SQLAlchemy
# connaisse toutes les classes au démarrage.
from app.models.country import Country
from app.models.operator import Operator
from app.models.route import Route
from app.models.trip import Trip
from app.models.station import Station
from app.models.stop import Stop
from app.models.city import City
from app.api.routes import prediction
# Import du routeur des trajets
from app.api.routes.trips import router as trips_router

# Import du routeur des stations
from app.api.routes.stations import router as stations_router

# Import du routeur des routes
from app.api.routes.routes import router as routes_router
from prometheus_fastapi_instrumentator import Instrumentator

# Création de l'application FastAPI
app = FastAPI(
    title="ObRail Europe API",
    description="API REST pour exploiter les données ferroviaires ObRail Europe",
    version="1.0.0",
)

# Ajouter le routeur des trajets
app.include_router(trips_router)
# Ajouter le routeur des stations
app.include_router(stations_router)

# Ajouter le routeur des routes
app.include_router(routes_router)
app.include_router(prediction.router)
Instrumentator().instrument(app).expose(app)

# Route principale de test
@app.get("/")
def root():
    # Retourne un message pour vérifier que l'API fonctionne
    return {
        "message": "ObRail Europe API fonctionne !"
    }