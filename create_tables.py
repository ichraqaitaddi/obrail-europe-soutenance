from app.database.database import engine
from app.database.base import Base

# Importer les modèles
from app.models.country import Country
from app.models.operator import Operator
from app.models.route import Route
from app.models.trip import Trip

# Importer le modèle Station pour permettre à SQLAlchemy de créer la table stations
from app.models.station import Station

# Importer le modèle Stop pour permettre à SQLAlchemy de créer la table stops
from app.models.stop import Stop
# Importer le modèle City pour permettre à SQLAlchemy de créer la table cities
from app.models.city import City


# Créer toutes les tables
Base.metadata.create_all(bind=engine)

print("Tables créées avec succès !")