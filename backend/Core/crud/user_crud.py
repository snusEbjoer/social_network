from Core.models.database import User
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from auth.jwt import hash_password
from Core.schemas.schemas import UserCreate


async def get_user_by_username(username: str, db: AsyncSession):
    user = await db.execute(select(User).where(User.username == username))
    return user.scalars().one_or_none()


async def create_user(user: UserCreate, db: AsyncSession):
    db_user = User(
        username=user.username, hashed_password=hash_password(user.password), posts=[]
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def delete_user(user: UserCreate, db: AsyncSession):
    db_user = db.execute(select(User).where(User.username == user.username))
    await db.delete(db_user)
    await db.commit()
    return db_user


async def get_user(user_id: int, db: AsyncSession):
    query = await db.execute(select(User).filter(User.id == user_id))
    return query.scalars().first()


async def get_user_posts(username: str, db: AsyncSession):
    query = await db.execute(select(User).filter(User.username == username))
    db_user = query.scalars().first()
    if db_user and db_user.posts:
        return db_user.posts
