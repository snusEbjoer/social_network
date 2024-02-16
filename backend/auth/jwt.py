from datetime import datetime, timedelta, timezone
import os
from xmlrpc.client import boolean
from fastapi import HTTPException, Request, status
from passlib.context import CryptContext
from sqlalchemy import false
from sqlalchemy.ext.asyncio import AsyncSession
from Core.schemas.schemas import *
from jose import JWTError, jwt
from dotenv import load_dotenv

from Core.models.database import User

load_dotenv()

bcrypt_context = CryptContext(schemes=["bcrypt"])
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
REFRESH_KEY= os.getenv("REFRESH_KEY")

def hash_password(password:str):
    return bcrypt_context.hash(password)

def verify_password(plain_password:str, hashed_password:str):
    return bcrypt_context.verify(plain_password, hashed_password)

def create_access_token(user: UserBase, expires_delta: timedelta | None):
    to_encode = user.__dict__.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({'exp':expire})
    access_token = jwt.encode(to_encode, key=SECRET_KEY, algorithm=ALGORITHM)
    print(to_encode, access_token, "access")
    return access_token

def create_refresh_token(user: UserBase):
    to_encode = user.__dict__.copy()
    to_encode.update({"exp": datetime.now(timezone.utc) + timedelta(days=1)})
    refresh_token = jwt.encode(to_encode, key=REFRESH_KEY, algorithm=ALGORITHM)
    return refresh_token

def auth_guard(func, db: AsyncSession, request: Request, return_user: boolean = False, ):
    def wrapper():
        try:
           header = request.headers.get("Authorization")
           if header and header.startswith("Bearer "):
            to_decode = header.removeprefix("Bearer ")
            user = jwt.decode(to_decode, key=SECRET_KEY, algorithms=ALGORITHM)
            username: str = user.get("username")
            db_user = db.query(User).filter(User.username == username).first()
            if db_user and return_user:
                return func(db_user)
            if db_user:
                return func()
        except:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        return wrapper