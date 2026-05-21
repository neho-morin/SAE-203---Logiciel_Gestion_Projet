from fastapi import Header, HTTPException, status


async def verify_token(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token manquant ou mal formé. Format attendu : Authorization: Bearer <token>",
        )
    token = authorization.removeprefix("Bearer ").strip()

    from config.settings import API_TOKEN
    if not API_TOKEN or token != API_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Token invalide.",
        )
