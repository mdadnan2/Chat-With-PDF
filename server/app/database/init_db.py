from app.database.base import Base
from app.database.session import engine

# Import models
from app.database.models import Document, Chunk

Base.metadata.create_all(bind=engine)