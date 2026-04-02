from fastapi import Header, HTTPException, status

from app.core.config import config

API_TOKEN = config["settings"].get("ncserv_api_token")


async def verify_token(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Token "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    token = authorization.split(" ", 1)[1]
    if not API_TOKEN or token != API_TOKEN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
