from datetime import datetime
from uuid import UUID
from pydantic import BaseModel
from typing import List, Optional

class PostBase(BaseModel):
  title: str
  content: str
  username: str
  created_at: datetime = datetime.now()

class PostCreate(PostBase):
  pass

class PostUpdate(BaseModel):
  title: str
  content: str

class Post(PostBase):
  id: UUID

  class Config:
    orm_mode = True
    from_attributes = True


class CommentBase(BaseModel):
  content: str
  username: str
  created_at: datetime = datetime.now()

class CommentCreate(CommentBase):
  pass

class CommentUpdate(BaseModel):
  content: str

class Comment(CommentBase):
  id: UUID

  class Config:
    orm_mode = True
    from_attributes = True


class LikeBase(BaseModel):
    username: str 

class LikeCreate(LikeBase):
  pass

class Like(LikeBase):
  id: UUID

  class Config:
    orm_mode = True
    from_attributes = True