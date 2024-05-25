from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends
from database import get_db
from routers import posts, comments
import models, schemas
from typing import List
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/api/v1/likes",
    tags=["likes"],
    responses={404: {"description": "Not found"}},
)

@router.post("/add/{post_id}", tags=["Likes"])
def like_post(post_id:UUID, like: schemas.LikeCreate, db = Depends(get_db)):
    if posts.post_exists(post_id, db):
        db_like = models.Like(username=like.username, post_id=post_id)
        db.add(db_like)
        db.commit()
        db.refresh(db_like)
    elif comments.comment_exists(post_id, db):
        db_like = models.Like(username=like.username, comment_id=post_id)
        db.add(db_like)
        db.commit()
        db.refresh(db_like)
    return db_like


@router.get("/get/{post_id}", response_model=List[schemas.Like])
def get_likes(post_id: UUID, db: Session = Depends(get_db)):
    post = posts.post_exists(post_id, db) or comments.comment_exists(post_id, db)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    likes = db.query(models.Like).filter(
        (models.Like.post_id == post_id) |
        (models.Like.comment_id == post_id)
    ).all()

    return likes

@router.get("/get/count/{post_id}", response_model=int)
def get_likes_count(post_id: UUID, db: Session = Depends(get_db)):
    post = posts.post_exists(post_id, db) or comments.comment_exists(post_id, db)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    likes = db.query(models.Like).filter(
        (models.Like.post_id == post_id) |
        (models.Like.comment_id == post_id)
    ).count()

    return likes