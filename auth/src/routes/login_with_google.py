from fastapi import APIRouter
from starlette.requests import Request
from fastapi_sso.sso.google import GoogleSSO
from dotenv import load_dotenv
import os

load_dotenv()

router = APIRouter()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
print(GOOGLE_CLIENT_ID)
print(GOOGLE_CLIENT_SECRET)

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

google_sso = GoogleSSO(
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET, 
    redirect_uri="http://medbot.xyz/api/auth/google/callback",
    allow_insecure_http=True
)

@router.get('/google/login')
async def login(request:Request):
    with google_sso:
        redirect_uri = request.url_for('google_callback')
        print("Redirect URI: ",redirect_uri)
        return await google_sso.get_login_redirect(redirect_uri=redirect_uri)

@router.get("/google/callback",name='google_callback')
async def callback(request:Request):
    with google_sso:
        user = await google_sso.verify_and_process(request)
    return user