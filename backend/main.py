from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from database import Base, engine
from routes.auth import router as auth_router
from routes.users import router as users_router
import model

app = FastAPI()
Base.metadata.create_all(bind=engine)
app.include_router(auth_router)
app.include_router(users_router)

@app.get('/')
def read_root():
    return {"Hello": "World"}
