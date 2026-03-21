from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# We'll use SQLite for local development as previously suggested
SQLALCHEMY_DATABASE_URL = "sqlite:///./f1_dashboard.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency to get db session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
