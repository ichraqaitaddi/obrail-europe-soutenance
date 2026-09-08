# Importer les types SQL nécessaires pour définir les colonnes
from sqlalchemy import String, ForeignKey

# Importer les outils SQLAlchemy permettant de définir les champs du modèle
from sqlalchemy.orm import Mapped, mapped_column, relationship

# Importer la classe Base qui sert de classe parent à nos modèles
from app.database.base import Base


# Modèle représentant un point d'arrêt dans la base de données
class Stop(Base):

    # Nom de la table correspondante dans PostgreSQL
    __tablename__ = "stops"

    # Identifiant interne du point d'arrêt
    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    # Identifiant du point d'arrêt provenant du fichier GTFS
    gtfs_stop_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True
    )

    # Nom du point d'arrêt provenant de stop_name
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    # Identifiant de la station principale à laquelle le point d'arrêt appartient
    # Il correspond à parent_station dans le fichier GTFS
    station_id: Mapped[int] = mapped_column(
        ForeignKey("stations.id"),
        nullable=False
    )

    # Relation avec la station principale
    station = relationship("Station")