from fastapi import APIRouter,Request
from dotenv import load_dotenv
from starlette.config import Config
from starlette.responses import RedirectResponse,HTMLResponse
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
    client_kwargs={"scope": "openid profile email"},
)




@router.route('/login-with-google')
async def login(request:Request):
    redirect_uri = request.url_for('google-callback')
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.route("/google-callback",name='google-callback')
async def callback(request:Request):
    try:
        token = await oauth.google.authorize_access_token(request)
    except OAuthError as error:
        return HTMLResponse(f'<h1>{error.error} afas</h1>')
    user = token.get('userinfo')
    if user:
        print(user)
        return {"working":"true"}
    return {"working":"false"}