import json
from typing import Dict, List, Optional
import httpx
from fastapi import Depends, FastAPI, HTTPException, Security
from fastapi.security import OAuth2AuthorizationCodeBearer
from jose import jwt, jwk
from jose.exceptions import JWTError
from pydantic import BaseModel
from ..schemas import schemas


KEYCLOAK_URL = "http://localhost:8080"
REALM_NAME = "fastapi-backend"
KEYCLOAK_CLIENT_ID = "fastapi-backend"
# _________________________
KEYCLOAK_ADMIN_USERNAME = "admin"
KEYCLOAK_ADMIN_PASSWORD = "admin"
KEYCLOAK_ADMIN_CLIENT_ID = "admin-cli"
# JWKs URL
JWKS_URL = f"{KEYCLOAK_URL}/realms/{REALM_NAME}/protocol/openid-connect/certs"


oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=f"{KEYCLOAK_URL}/realms/{REALM_NAME}/protocol/openid-connect/auth",
    tokenUrl=f"{KEYCLOAK_URL}/realms/{REALM_NAME}/protocol/openid-connect/token",
    auto_error=False
)

async def validate_token(token: str) -> schemas.KeycloakToken:
    try:
        # Fetch JWKS
        async with httpx.AsyncClient() as client:
            response = await client.get(JWKS_URL)
            response.raise_for_status()
            jwks = response.json()
        
        # Decode the token headers to get the key ID
        headers = jwt.get_unverified_headers(token)
        kid = headers.get("kid")
        if not kid:
            raise HTTPException(status_code=401, detail="Token missing 'kid' header")
        
        # Find the correct key in the JWKS
        key_data = next((key for key in jwks["keys"] if key["kid"] == kid), None)
        if not key_data:
            raise HTTPException(status_code=401, detail="Matching key not found in JWKS")
        
        # Convert JWK to RSA public key
        public_key = jwk.construct(key_data).public_key()
        
        # Verify the token
        payload = jwt.decode(
            token, 
            key=public_key, 
            algorithms=["RS256"], 
            audience="account"  # Ensure this matches the 'aud' claim in your token
        )
        
        # Extract username and roles
        username = payload.get("preferred_username")
        roles = payload.get("realm_access", {}).get("roles", [])
        if not username or not roles:
            raise HTTPException(status_code=401, detail="Token missing required claims")
        
        return schemas.KeycloakToken(username=username, roles=roles)
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

async def get_current_user(token: str = Depends(oauth2_scheme)):
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return await validate_token(token)

def has_role(required_role:str):
    def role_checker(token: schemas.KeycloakToken = Depends(get_current_user)) -> schemas.KeycloakToken:
        if required_role not in token.roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return token
    return role_checker


async def get_keycloak_admin_token() -> str:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{KEYCLOAK_URL}/realms/master/protocol/openid-connect/token",
            data={
                "grant_type": "password",
                "client_id": KEYCLOAK_ADMIN_CLIENT_ID,
                "username": KEYCLOAK_ADMIN_USERNAME,
                "password": KEYCLOAK_ADMIN_PASSWORD,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        response.raise_for_status()
        return response.json()["access_token"]