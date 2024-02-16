import os
from dotenv import load_dotenv
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Float, create_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import relationship, sessionmaker, mapped_column, Mapped
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs, AsyncSession
from sqlalchemy.sql import func
from typing import List

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
print(DATABASE_URL)

engine = create_async_engine(url=DATABASE_URL)
SessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

class Base(AsyncAttrs, DeclarativeBase):
    pass

async def get_db():
  db = SessionLocal()
  try:
    yield db
  finally:
    await db.close()

class User(Base):
  __tablename__ = "user"
  id: Mapped[int] = mapped_column(primary_key=True)
  username: Mapped[str] = mapped_column(String, unique=True)
  hashed_password: Mapped[str] = mapped_column(String)
  posts: Mapped[List["Post"]] = relationship()

class Post(Base):
  __tablename__ = "post"
  id: Mapped[int] = mapped_column(primary_key=True)
  title: Mapped[str] = mapped_column(String)
  previewText: Mapped[str] = mapped_column(String)
  fullText: Mapped[str] = mapped_column(String)
  author_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
  comments: Mapped[List["Comment"]] = relationship()
  likes: Mapped[List["Like"]] = relationship()

class Comment(Base):
  __tablename__ = "comment"
  id: Mapped[int] = mapped_column(primary_key=True)
  text: Mapped[str] = mapped_column(String)
  author_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
  author_username: Mapped[str] = mapped_column(String)
  post_id: Mapped[int] = mapped_column(ForeignKey("post.id"))

class Like(Base):
  __tablename__ = "like"
  id: Mapped[int] = mapped_column(primary_key=True)
  user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
  post_id: Mapped[int] = mapped_column(ForeignKey("post.id"))