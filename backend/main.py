from fastapi import FastAPI
from database import Base, engine
import model

app = FastAPI()
Base.metadata.create_all(bind=engine)

@app.get('/')
def read_root():
    return {"Hello": "World"}
