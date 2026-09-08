from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

class Trip(Base):
    __tablename__ = "trips"

    # Identifiant interne de notre base PostgreSQL
    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    # Identifiant original provenant du fichier GTFS
    gtfs_trip_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True
    )

    # Référence vers la route à laquelle appartient ce trip
    route_id: Mapped[int] = mapped_column(
        ForeignKey("routes.id"),
        nullable=False
    )

    # Identifiant du service associé au trip
    service_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
        # Destination ou indication affichée pour le trajet
    headsign: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )
        # Direction du trajet
    direction_id: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )
        # Relation avec la route associée à ce trip
    route = relationship("Route", back_populates="trips")