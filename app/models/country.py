from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Country(Base):
    __tablename__ = "countries"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True
    )

    iso_code: Mapped[str] = mapped_column(
        String(2),
        nullable=False,
        unique=True
    )

    operators = relationship("Operator", back_populates="country")