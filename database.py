
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./wallet.db"

engine = create_engine(DATABASE_URL, echo=True, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

session = sessionmaker(SessionLocal)

Base = declarative_base()


def get_db():
    db = session()
    try:
        yield db
    finally:
        db.close()

def create_db_and_tables():
    print("Creating tables...")
    Base.metadata.create_all(engine)
    print("Tables created successfully")