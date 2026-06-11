from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from database import Base, engine
from routes.auth import router as auth_router
from routes.users import router as users_router
from routes.board import router as board_router
import model

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
Base.metadata.create_all(bind=engine)
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(board_router)

@app.get('/')
def read_root():
    return {"Hello": "World"}
