import sys
from datetime import datetime, timedelta, timezone
import os
from passlib.context import CryptContext
from jose import jwt
from dotenv import load_dotenv

from Core.schemas.schemas import UserBase

load_dotenv()

bcrypt_context = CryptContext(schemes=["bcrypt"])
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
REFRESH_KEY = os.getenv("REFRESH_KEY")
if SECRET_KEY is None or ALGORITHM is None or REFRESH_KEY is None:
    sys.stderr.write("You should provide all variables in .env file")
    exit(1)


def hash_password(password: str):
    return bcrypt_context.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    return bcrypt_context.verify(plain_password, hashed_password)


def create_access_token(user: UserBase, expires_delta: timedelta | None):
    to_encode = user.__dict__.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    access_token = jwt.encode(to_encode, key=SECRET_KEY, algorithm=ALGORITHM)
    print(to_encode, access_token, "access")
    return access_token


def create_refresh_token(user: UserBase):
    to_encode = user.__dict__.copy()
    to_encode.update({"exp": str(datetime.now(timezone.utc) + timedelta(days=1))})
    refresh_token = jwt.encode(to_encode, key=REFRESH_KEY, algorithm=ALGORITHM)
    return refresh_token
