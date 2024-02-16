from typing import NoReturn
from Core.schemas.schemas import UserBase, UserCreate, UserResponce
from Core.models.database import Post
from sqlalchemy.orm import Session

def create_post(token:str ,text:str, db:Session):
  