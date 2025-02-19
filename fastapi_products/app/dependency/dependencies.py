import requests
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

DJANGO_AUTH_URL = "http://127.0.0.1:8000/api/check-token/"

def get_current_user(token: str = Depends(oauth2_scheme)):
    headers = {"Authorization": f"Token {token}"}
    response = requests.get(DJANGO_AUTH_URL, headers=headers)

    if response.status_code != 200:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user_data = response.json()
    return str(user_data["user_id"])