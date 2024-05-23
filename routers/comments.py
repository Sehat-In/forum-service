from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends
from database import get_db
from sqlalchemy.orm import Session
import models
from starlette import status
from typing import List
import schemas
from routers import posts

router = APIRouter(
    prefix="/comments",
    tags=["comments"],
    responses={404: {"description": "Not found"}},
)

@router.post("/create/{post_id}", status_code=status.HTTP_201_CREATED, response_model=schemas.Comment)
def create_comment(post_id:UUID, comment: schemas.CommentCreate, db = Depends(get_db)):
  if posts.post_exists(post_id, db):
    db_comment = models.Comment(content=comment.content, username=comment.username, parent_post_id=post_id)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
  elif comment_exists(post_id, db):
    db_comment = models.Comment(content=comment.content, username=comment.username, parent_comment_id=post_id)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
  return db_comment

@router.get("/get/{post_id}", response_model=List[schemas.Comment])
def get_comments(post_id: UUID, db: Session = Depends(get_db)):
    post = posts.post_exists(post_id, db) or comment_exists(post_id, db)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    comments = db.query(models.Comment).filter(
        (models.Comment.parent_post_id == post_id) |
        (models.Comment.parent_comment_id == post_id)
    ).all()

    return comments

@router.delete("/delete/{comment_id}")
def delete_comment(comment_id: UUID, db = Depends(get_db)):
    db_comment = comment_exists(comment_id, db)
    db.delete(db_comment)
    db.commit()
    return db_comment

@router.put("/update/{comment_id}", response_model=schemas.Comment)
def update_comment(comment_id: UUID, comment: schemas.CommentUpdate, db = Depends(get_db)):
    db_comment = comment_exists(comment_id, db)
    db_comment.content = comment.content
    db.commit()
    db.refresh(db_comment)
    return db_comment
    

def comment_exists(comment_id: UUID, db: Session):
    comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    return comment