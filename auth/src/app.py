from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from .routes.main import router
from .database.config import Base,engine
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
import json


import os


Base.metadata.create_all(bind=engine)
SECRET_KEY = os.getenv('SECRET_KEY')
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")


app = FastAPI(root_path="/api/auth")
# app.add_middleware(
#     # CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"]
# )


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        body = await request.body()
        print(f"Request body: {body.decode()}")
        print(f"Request headers: {dict(request.headers)}")
        print(f"Request path: {request.url.path}")
        response = await call_next(request)
        print(f"Response status: {response.status_code}")
        return response

app.add_middleware(LoggingMiddleware)
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)
app.include_router(router=router)


@app.get('/')
async def root():
    return {"message":"Hello from auth service."}
