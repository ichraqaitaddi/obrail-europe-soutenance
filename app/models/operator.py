from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Operator(Base):
    __tablename__ = "operators"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Identifiant provenant de la source GTFS
    gtfs_agency_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True
    )

    website: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    country_id: Mapped[int] = mapped_column(
        ForeignKey("countries.id"),
        nullable=False
    )

    country = relationship("Country", back_populates="operators")
    # Liste des routes appartenant à cet opérateur
    routes = relationship("Route", back_populates="operator")