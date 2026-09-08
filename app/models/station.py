# Importer les types SQL nécessaires pour définir les colonnes
from sqlalchemy import String, Float, ForeignKey

# Importer les outils SQLAlchemy permettant de définir les champs
# et les relations entre les modèles
from sqlalchemy.orm import Mapped, mapped_column, relationship

# Importer la classe Base qui sert de classe parent à nos modèles
from app.database.base import Base


# Modèle représentant une station ferroviaire dans la base de données
class Station(Base):

    # Nom de la table correspondante dans PostgreSQL
    __tablename__ = "stations"

    # Identifiant interne de la station
    # Il est généré automatiquement par PostgreSQL
    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    # Identifiant de la station provenant du fichier GTFS (stop_id)
    # Il doit être unique dans notre base
    gtfs_stop_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True
    )

    # Nom de la station provenant de la colonne stop_name
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    # Latitude de la station provenant de stop_lat
    latitude: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    # Longitude de la station provenant de stop_lon
    longitude: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    # Identifiant interne de la ville à laquelle appartient la station
    # Il correspond à la clé primaire de la table cities
    city_id: Mapped[int] = mapped_column(
        ForeignKey("cities.id"),
        nullable=True
    )

    # Relation entre une station et sa ville
    #
    # Une station peut être associée à une ville.
    # Grâce à cette relation, on peut utiliser :
    #
    # station.city
    #
    # pour récupérer directement l'objet City associé.
    city = relationship("City")