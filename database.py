import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv()

SQLALCHEMY_DATABASE_URL = 'postgresql://' + os.getenv("DATABASE_USER") + ':' + os.getenv("DATABASE_PASSWORD") + '@' + os.getenv("DATABASE_HOST") + ':' + str(os.getenv("DATABASE_PORT")) + '/' + os.getenv("DATABASE_NAME")

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
  db = SessionLocal()
  try:
    print("connected to database")
    yield db
  finally:
    print("closing database connection")
    db.close()