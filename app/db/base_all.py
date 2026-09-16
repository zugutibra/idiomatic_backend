"""Imports every model so Base.metadata is complete for Alembic autogenerate
and for scripts that call Base.metadata.create_all()."""

from app.db.base import Base  # noqa: F401
from app.models.idiom import Idiom  # noqa: F401
from app.models.progress import UserIdiomProgress  # noqa: F401
from app.models.user import User  # noqa: F401
