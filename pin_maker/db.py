from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pin_maker.config import SQLALCHEMY_DATABASE_URI

engine = create_engine(SQLALCHEMY_DATABASE_URI)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
