import os
import requests
from jose import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv

from core.models import UserContext

load_dotenv()

TENANT_ID = os.getenv("AZURE_TENANT_ID", "")
API_AUDIENCE = os.getenv("AZURE_API_AUDIENCE", "")

JWKS_URL = f"https://login.microsoftonline.com/{TENANT_ID}/discovery/v2.0/keys"
ISSUER = f"https://sts.windows.net/{TENANT_ID}/"

http_bearer = HTTPBearer()
_jwks = requests.get(JWKS_URL).json()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
) -> UserContext:
    token = credentials.credentials
    try:
        header = jwt.get_unverified_header(token)
        kid = header["kid"]
        key = next(k for k in _jwks["keys"] if k["kid"] == kid)

        claims = jwt.decode(
            token,
            key,
            algorithms=["RS256"],
            audience=API_AUDIENCE,
            issuer=ISSUER,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {exc}",
        )

    user_id = claims.get("oid") or claims.get("sub")
    display_name = claims.get("name") or claims.get("preferred_username")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing oid/sub",
        )

    return UserContext(
        id=user_id,
        display_name=display_name or user_id,
        roles=["admin"],
    )
