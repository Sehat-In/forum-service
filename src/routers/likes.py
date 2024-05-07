from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.routers import posts, comments

router = APIRouter(
    prefix="/likes",
    tags=["likes"],
    responses={404: {"description": "Not found"}},
)

class Like(BaseModel):
    post_id: str 
    likes: int

likes = {}

@router.post("/{post_id}", tags=["Likes"])
def like_post(post_id: str):
    if not posts.post_exists(post_id) or not comments.comment_exists(post_id):
        raise HTTPException(status_code=404, detail="Post not found")
    if post_id not in likes:
        likes[post_id] = 1
    else:
        likes[post_id] += 1
    
    return {"message": "Post liked successfully"}

@router.get("/{post_id}", tags=["Likes"])
def get_likes(post_id: str):
    if not (posts.post_exists(post_id) or comments.comment_exists(post_id)):
        raise HTTPException(status_code=404, detail="Post not found")
    return {"likes": likes.get(post_id, 0)}