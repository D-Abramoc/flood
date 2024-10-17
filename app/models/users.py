from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.config import settings
from app.database import Base


class User(Base):
    name: Mapped[str] = mapped_column(
        String(length=settings.max_length_string),
        nullable=False
    )
    password: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False)
