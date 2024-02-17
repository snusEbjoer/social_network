from typing import List
from pydantic import BaseModel


class Like(BaseModel):
    id: int
    user_id: int
    post_id: int


class Comment(BaseModel):
    id: int
    text: str
    author_id: int
    author_username: str
    post_id: int


class Post(BaseModel):
    id: int
    title: str
    previewText: str
    fullText: str
    author_id: int
    comments: List[Comment]
    likes: List[Like]


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str


class UserResponce(UserBase):
    id: int
    posts: List[Post]
