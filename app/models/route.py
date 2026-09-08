from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Route(Base):
    __tablename__ = "routes"

    # Identifiant interne de notre base PostgreSQL
    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    # Identifiant original provenant du fichier GTFS
    gtfs_route_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True
    )
        # Nom court de la route
    short_name: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )
        # Nom complet de la route
    long_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )
        # Référence vers l'opérateur propriétaire de cette route
    operator_id: Mapped[int] = mapped_column(
        ForeignKey("operators.id"),
        nullable=False
    )

    # Relation avec le modèle Operator
    operator = relationship("Operator", back_populates="routes")
    # Liste des trips appartenant à cette route
    trips = relationship("Trip", back_populates="route")