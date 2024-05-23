from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends
from database import get_db
from sqlalchemy.orm import Session
import models
from starlette import status
from typing import List
import schemas

router = APIRouter(
    prefix="/posts",
    tags=["posts"],
    responses={404: {"description": "Not found"}},
)

@router.post("/create", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_post(post: schemas.PostCreate, db = Depends(get_db)):
    db_post = models.Post(title=post.title, content=post.content, username=post.username)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

@router.get("/get/all", response_model=List[schemas.Post])
def get_posts(db = Depends(get_db)):
    return db.query(models.Post).all()


@router.get("/get/{post_id}", response_model=schemas.Post)
def get_post(post_id: UUID, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return schemas.Post.from_orm(post)

@router.delete("/delete/{post_id}")
def delete_post(post_id: UUID, db = Depends(get_db)):
    db_post = post_exists(post_id, db)
    db.delete(db_post)
    db.commit()
    return db_post

@router.put("/update/{post_id}", response_model=schemas.Post)
def update_post(post_id: UUID, post: schemas.PostUpdate, db = Depends(get_db)):
    db_post = post_exists(post_id, db)
    db_post.title = post.title
    db_post.content = post.content
    db.commit()
    db.refresh(db_post)
    return db_post

def post_exists(post_id: UUID, db: Session):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    return post