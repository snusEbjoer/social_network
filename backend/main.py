from fastapi import Depends, FastAPI, APIRouter, Request
import uvicorn
from dotenv import load_dotenv
from fastapi_sqlalchemy import DBSessionMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import os,sys
from Core.models.database import get_db
from routers import user
from Core.models.database import User
from jose import jwt

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

app = FastAPI()
router = APIRouter()
app.include_router(user.router)
# to avoid csrftokenError
app.add_middleware(DBSessionMiddleware, db_url=DATABASE_URL)


@app.middleware("http")
async def app_auth_middleware(request:Request, call_next):
    db = get_db()
    header = request.headers.get("Authorization")
    if header and header.startswith("Bearer "):
        to_decode = header.removeprefix("Bearer ")
        user = jwt.decode(to_decode, key=SECRET_KEY, algorithms=ALGORITHM) # type: ignore
        username: str = user.get("username") # type: ignore
        db_user = await db.execute(select(User).where(User.username == username))
        request.scope["user"] = db_user.scalars().one()
        return call_next(request)


@app.get("/")
async def root():
    return {"message": "hello world"}

if __name__ == '__main__':
    uvicorn.run(app, port=8000, reload=True)