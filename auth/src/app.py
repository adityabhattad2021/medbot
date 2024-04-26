from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from .routes.main import router
from .database.config import Base,engine
import os

Base.metadata.create_all(bind=engine)

SECRET_KEY = os.getenv('SECRET_KEY')

app = FastAPI(root_path="/api/auth")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)
app.include_router(router=router)


@app.get('/')
async def root():
    return {"message":"Hello from auth service."}
