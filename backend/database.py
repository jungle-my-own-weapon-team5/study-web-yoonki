import os
from dotenv import load_dotenv

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

load_dotenv()
os.getenv('VAR_NAME')

username=os.getenv('DB_USER')
password=os.getenv('DB_PASSWORD')
host=os.getenv('DB_HOST')
port=os.getenv('DB_PORT')
db_name=os.getenv('DB_NAME')

engine = create_engine(f'postgresql://{username}:{password}@{host}:{port}/{db_name}')
session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Base = declarative_base()

def get_db():
    db = session()
    try:
        yield db
    finally:
        db.close()
