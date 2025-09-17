from sqlmodel import create_engine, Session
from app.utils.core.config import settings

# Construction de l'URL de connexion à partir des variables d'environnement
DATABASE_URL = f"postgresql://{settings.DB_USERNAME}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_DATABASE}"

engine = create_engine(DATABASE_URL, echo=settings.DEBUG)


def get_db():
    """Dependency to get database session"""
    with Session(engine) as session:
        yield session
