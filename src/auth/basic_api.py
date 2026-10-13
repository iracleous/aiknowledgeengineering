"""
Below is a single-file FastAPI example with:
- POST /login: checks credentials and returns a JWT.
- GET /public: accessible without login.
- GET /protected: requires a valid JWT.
- GET /users/me: returns the authenticated user.

uv add fastapi uvicorn pyjwt "pwdlib[argon2]" python-multipart python-dotenv
"""

import os
from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from pydantic import BaseModel
from uvicorn import run


load_dotenv()

SECRET_KEY = os.environ["JWT_SECRET_KEY"]
ALGORITHM = "HS256"
ACCESS_TOKEN_MINUTES = 30

app = FastAPI(title="Login and JWT Example")

password_hash = PasswordHash.recommended()

# Reads the token from:
# Authorization: Bearer <token>
# Also enables the Authorize button in Swagger.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


class Token(BaseModel):
    access_token: str
    token_type: str


class User(BaseModel):
    username: str
    full_name: str


# Demo user store. Replace with a database in a real application.
# The password is hashed; it is never included in API responses.
users_db = {
    "student": {
        "username": "student",
        "full_name": "Demo Student",
        "hashed_password": password_hash.hash("Student123!"),
    }
}

# Used when the username does not exist.
dummy_hash = password_hash.hash("unused-demo-password")


def unauthorized() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials or token",
        headers={"WWW-Authenticate": "Bearer"},
    )


def create_access_token(username: str) -> str:
    now = datetime.now(timezone.utc)

    payload = {
        "sub": username,
        "iat": now,
        "exp": now + timedelta(minutes=ACCESS_TOKEN_MINUTES),
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
) -> User:
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
            options={"require": ["sub", "iat", "exp"]},
        )

        username = payload["sub"]

        if not isinstance(username, str):
            raise unauthorized()

    except InvalidTokenError:
        # Includes invalid signatures and expired tokens.
        raise unauthorized()

    user = users_db.get(username)

    if user is None:
        raise unauthorized()

    return User(
        username=user["username"],
        full_name=user["full_name"],
    )


@app.post("/login", response_model=Token)
def login(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
):
    user = users_db.get(form.username)

    stored_hash = (
        user["hashed_password"] if user else dummy_hash
    )
    valid_password = password_hash.verify(
        form.password,
        stored_hash,
    )

    if user is None or not valid_password:
        raise unauthorized()

    return Token(
        access_token=create_access_token(user["username"]),
        token_type="bearer",
    )


@app.get("/public")
def public_endpoint():
    return {
        "message": "Anyone can access this endpoint."
    }


@app.get("/protected")
def protected_endpoint(
    current_user: Annotated[User, Depends(get_current_user)],
):
    return {
        "message": f"Welcome, {current_user.username}!",
        "data": "This information requires authentication.",
    }


@app.get("/users/me", response_model=User)
def read_current_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    return current_user


if __name__ == "__main__":
    run(app, host="0.0.0.0", port=8000)

