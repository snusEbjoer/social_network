import os
import sys
from datetime import timedelta
from typing import Annotated
from typing_extensions import TypedDict
from fastapi import APIRouter, Depends, HTTPException, Request, status
from Core.models.database import get_db
from dotenv import load_dotenv
from passlib.context import CryptContext
from pydantic import BaseModel
from Core.models.database import User
from sqlalchemy.ext.asyncio import AsyncSession
from auth.jwt import (
    create_access_token,
    create_refresh_token,
    verify_password,
)
from Core.crud import user_crud
from Core.schemas.schemas import UserBase, UserCreate, UserResponce
from jose import JWTError, jwt

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
REFRESH_KEY = os.getenv("REFRESH_KEY")

if SECRET_KEY is None or ALGORITHM is None or REFRESH_KEY is None:
    sys.stderr.write("You should provide all variables in .env file")
    exit(1)

bcrypt_context = CryptContext(schemes=["bcrypt"])
router = APIRouter(prefix="/user")


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class UserCredentials(TypedDict):
    username: str
    password: str


class RefreshToken(BaseModel):
    refresh_token: str


def extract_token(request: Request):
    token = request.headers.get("Authorization")
    if token is not None and token.startswith("Bearer "):
        return token.removeprefix("Bearer ")
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unauthorized",
        headers={"WWW-Authenticate": "Bearer"},
    )


def to_valid_responce_type(user: User):
    return


@router.post("/signUp/", tags=["user"], response_model=UserResponce)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    if await user_crud.get_user_by_username(user.username, db):
        raise HTTPException(status_code=400, detail="Username alredy taken")

    print(user)
    db_user = await user_crud.create_user(user, db)
    return db_user


@router.post("/login/", tags=["user"], response_model=Token)
async def login_user(user: UserCreate, db: AsyncSession = Depends(get_db)) -> Token:
    db_user = await user_crud.get_user_by_username(user.username, db)
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    access_token_expire = timedelta(minutes=30)
    access_token = create_access_token(
        UserBase(username=user.username), access_token_expire
    )
    refresh_token = create_refresh_token(user)
    return Token(
        access_token=access_token, refresh_token=refresh_token, token_type="Bearer"
    )


@router.get(path="/current", tags=["user"], response_model=UserResponce)
def get_current_user(
    token: Annotated[str, Depends(extract_token)],
    db: AsyncSession = Depends(get_db),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token_data = jwt.decode(token, key=SECRET_KEY, algorithms=ALGORITHM)
        username: str = str(token_data.get("username"))
    except JWTError:
        raise credentials_exception
    if username is None:
        raise credentials_exception
    user = user_crud.get_user_by_username(username, db)
    if user is None:
        raise credentials_exception
    return user


@router.get(path="/refresh", tags=["user"], response_model=Token)
def refresh_access_token(body: RefreshToken, db: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    if body.refresh_token is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid body"
        )
    try:
        token_data = jwt.decode(
            body.refresh_token, key=REFRESH_KEY, algorithms=ALGORITHM
        )
        username: str = token_data["username"]
    except JWTError:
        raise credentials_exception
    user = user_crud.get_user_by_username(username, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    access_token = create_access_token(
        UserBase(username=username), expires_delta=timedelta(minutes=30)
    )
    refresh_token = create_refresh_token(UserBase(username=username))
    return Token(
        access_token=access_token, refresh_token=refresh_token, token_type="Bearer"
    )


@router.get(path="/{username}", tags=["user"])
async def get_user_by_username(username: str, db: AsyncSession = Depends(get_db)):
    user = await user_crud.get_user_by_username(username, db)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user
