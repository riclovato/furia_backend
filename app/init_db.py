from .database import engine
from .models import Base

def init_db():
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
