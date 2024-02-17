import sys
from fastapi import FastAPI, APIRouter, Request
import uvicorn
from dotenv import load_dotenv
from fastapi_sqlalchemy import DBSessionMiddleware
from sqlalchemy import select
import os
from Core.models.database import SessionLocal
from routers import user
from Core.models.database import User
from jose import jwt

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

if DATABASE_URL is None or SECRET_KEY is None or ALGORITHM is None:
    sys.stderr.write("You should provide all variables in .env file")
    exit(1)

app = FastAPI()
router = APIRouter()
app.include_router(user.router)
app.add_middleware(DBSessionMiddleware, db_url=DATABASE_URL)


def extract_token(header_string: str) -> str | None:
    parts = header_string.split(" ")
    if len(parts) != 2:
        return
    prefix, token = parts
    if prefix != "Bearer":
        return
    return token


@app.middleware("http")
async def app_auth_middleware(request: Request, call_next):
    db = SessionLocal()
    try:
        header = request.headers.get("Authorization")
        if header is None:
            return await call_next()

        token = extract_token(header)
        if token is None:
            return await call_next()

        payload = jwt.decode(token, key=SECRET_KEY, algorithms=ALGORITHM)
        db_user = await user.get_user_by_username(payload["username"])
        request.scope["user"] = db_user
        return await call_next(request)
    finally:
        await db.close()


@app.get("/")
async def root():
    return {"message": "hello world"}


if __name__ == "__main__":
    uvicorn.run(app, port=8000, reload=True)
