from datetime import datetime
import os
from uuid import UUID
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Depends
from database import get_db
from sqlalchemy.orm import Session
import models
from starlette import status
from typing import List
import schemas
from routers import posts
import pika

load_dotenv()

router = APIRouter(
    prefix="/api/v1/comments",
    tags=["comments"],
    responses={404: {"description": "Not found"}},
)

@router.post("/create/{post_id}", status_code=status.HTTP_201_CREATED, response_model=schemas.Comment)
def create_comment(post_id:UUID, comment: schemas.CommentCreate, db = Depends(get_db)):
  post = posts.post_exists(post_id, db)
  if post:
    db_comment = models.Comment(content=comment.content, username=comment.username, parent_post_id=post_id, parent_comment_id=None)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    send_notification(post, comment.username)
  temp = comment_exists(post_id, db)
  if temp:
    db_comment = models.Comment(content=comment.content, username=comment.username, parent_comment_id=temp.id, parent_post_id=temp.parent_post_id)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)

    post = posts.post_exists(temp.parent_post_id, db)
    send_notification(post, comment.username)
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

@router.get("/get-comment/{comment_id}", response_model=schemas.Comment)
def get_comment(comment_id: UUID, db: Session = Depends(get_db)):
    comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Post not found")
    return comment

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

def send_notification(post: models.Post, comment_username: str):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=os.getenv('RABBITMQ_SERVER'), credentials=pika.PlainCredentials(os.getenv('RABBITMQ_USERNAME'), os.getenv('RABBITMQ_PASSWORD'))))
    channel = connection.channel()
    channel.basic_publish(exchange=f'notification_{post.id}', routing_key='', body=f'{post.id};{post.title};{comment_username};{datetime.now()}')
    connection.close()
