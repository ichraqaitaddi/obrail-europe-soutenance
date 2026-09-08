# Importer les types SQL nécessaires pour définir les colonnes
from sqlalchemy import String

# Importer les outils SQLAlchemy permettant de définir les champs du modèle
from sqlalchemy.orm import Mapped, mapped_column

# Importer la classe Base qui sert de classe parent à nos modèles
from app.database.base import Base


# Modèle représentant une ville dans la base de données
class City(Base):

    # Nom de la table correspondante dans PostgreSQL
    __tablename__ = "cities"

    # Identifiant interne de la ville
    # Il est généré automatiquement par PostgreSQL
    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    # Identifiant de la ville provenant de GeoNames
    # Il permettra d'identifier de manière unique une ville
    geonames_id: Mapped[int] = mapped_column(
        nullable=False,
        unique=True
    )

    # Nom de la ville
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    # Code ISO du pays
    # Exemple : ES pour Espagne, DE pour Allemagne
    country_code: Mapped[str] = mapped_column(
        String(2),
        nullable=False
    )