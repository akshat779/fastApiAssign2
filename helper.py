/To Login

@router.post("/login")
async def login(
        tenant: str,
        username: Annotated[EmailStr, Form()], password: Annotated[str, Form()], db: AsyncSession = Depends(get_db)
):
    authenticated_user = await authenticate_user(db , username, password, tenant)
    return authenticated_user
------------
 async def authenticate_user(db: AsyncSession, username: str, password: str, tenant: str):
    """Fetch access token from Keycloak."""
    async with AsyncClient() as client:
        keycloak_token_url = settings.KEYCLOAK_base_url.format(realm=tenant,endpoint="token")
        client_id = settings.KEYCLOAK_CLIENT_ID.format(realm=tenant)
        client_secret = await get_client_secret(tenant, client_id)
        org_details = await crud_organization.organization_crud.get_by_name(db, tenant)
        response = await client.post(
            keycloak_token_url,
            data={
                "grant_type": "password",
                "client_id": client_id,
                "client_secret": client_secret,
                "username": username,
                "password": password,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        if response.status_code != 200:
            print(f"Error: {response.status_code} - {response.text}")  # Log the response
            raise HTTPException(
                status_code=response.status_code, detail=response.json()
            )
        user_details = response.json()
        user_details['organization_id'] = org_details.id
        return user_details

---KEYCLOAK_base_url = <a href="http://keycloak:8080/realms/%7Brealm%7D/protocol/openid-connect/%7Bendpoint" rel="noreferrer noopener" title="http://keycloak:8080/realms/%7brealm%7d/protocol/openid-connect/%7bendpoint" target="_blank">http://keycloak:8080/realms/{realm}/protocol/openid-connect/{endpoint</a>}







/TO Decode the access token


try:
        # Extract the Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise ValueError("Invalid or missing Authorization header")

        # Extract the token
        token = auth_header[len("Bearer "):]

        # Decode the token without verification to extract the tenant ID
        unverified_payload = jwt.decode(token, options={"verify_signature": False})
        issuer_url = unverified_payload.get("iss")
        if not issuer_url:
            raise ValueError("Issuer URL not found in token")

        realm_index = issuer_url.find("/realms/")
        if realm_index == -1:
            raise ValueError("Tenant ID not found in token")
        tenant_id = issuer_url[realm_index + len("/realms/"):]

        # Construct the JWKS URL using the tenant ID
        jwks_url = f'{global_settings.keycloak_domain}/realms/{tenant_id}/protocol/openid-connect/certs'
        jwks_client = PyJWKClient(jwks_url)

        # Retrieve the signing key
        signing_key = jwks_client.get_signing_key_from_jwt(token).key

        # Decode and verify the token
        payload = jwt.decode(
            token,
            signing_key,
            algorithms=global_settings.keycloak_algorithm,
            audience=global_settings.keycloak_audience,
            issuer=global_settings.keycloak_domain + "/realms/" + tenant_id,
        )

    except (jwt.exceptions.PyJWKClientError, jwt.exceptions.DecodeError, jwt.exceptions.ExpiredSignatureError, ValueError) as error:
        # Handle decoding errors
        return JSONResponse({"status": "error", "message": str(error)}, status_code=401)






















