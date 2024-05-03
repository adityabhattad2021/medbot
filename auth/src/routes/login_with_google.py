from fastapi import APIRouter
from starlette.requests import Request
from dotenv import load_dotenv
from starlette.config import Config
from starlette.responses import JSONResponse,HTMLResponse
from authlib.integrations.starlette_client import OAuth,OAuthError
import os

load_dotenv()

router = APIRouter()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
SECRET_KEY = os.getenv('SECRET_KEY')

config = {
    "GOOGLE_CLIENT_ID": GOOGLE_CLIENT_ID,
    "GOOGLE_CLIENT_SECRET": GOOGLE_CLIENT_SECRET
}
starlette_config = Config(environ=config)
oauth = OAuth(starlette_config)
oauth.register(
    name="google",
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={'scope': 'openid email profile'},
)




@router.get('/login-with-google')
async def login(request:Request):
    redirect_uri = request.url_for('callback')
    authorization_url= await oauth.google.authorize_redirect(request, redirect_uri)
    return authorization_url

@router.get("/google-callback",name='callback')
async def callback(request:Request):
    try:
        token = await oauth.google.authorize_access_token(request)
        print("Token: ",token)
        user = token['userinfo']
    except Exception as error:
        print("Error: ",error.error)
        return JSONResponse({"working":"false"})
    if user:
        print(user)
        return JSONResponse({"working":"true"})
    return JSONResponse({"working":"false"})