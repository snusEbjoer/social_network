from pydantic import BaseModel
from Core.models.database import User
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from auth.jwt import hash_password
from Core.schemas.schemas import UserBase, UserCreate, UserResponce
from Core.models.database import Post

async def get_user_by_username(username:str, db: AsyncSession):
    user = await db.execute(select(User).where(User.username == username))
    return user.scalars().one()

async def create_user(user: UserCreate, db: AsyncSession):
    db_user = User(username=user.username, hashed_password=hash_password(user.password))
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def delete_user(user: UserCreate, db: AsyncSession):
    db_user = db.execute(select(User).where(User.username == user.username))
    await db.delete(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

def get_user(user_id: int, db:AsyncSession):
    db_user = db.query(User).filter(User.id == user_id).first()
    return db_user

def get_user_posts(username:str, db: AsyncSession):
    db_user = db.query(User).filter(User.username == username).first()
    if db_user and db_user.posts:
        return db_user.posts