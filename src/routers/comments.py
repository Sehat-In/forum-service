from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from src.routers import posts
from typing import List
import uuid
from datetime import datetime

router = APIRouter(
    prefix="/comments",
    tags=["comments"],
    responses={404: {"description": "Not found"}},
)

class Comment(BaseModel):
    id: str 
    content: str
    author: str
    parent_post_id: str
    created_at: datetime = datetime.now()

comments = []

@router.post("/{post_id}", response_model=Comment, tags=["Comments"])
def create_comment(post_id:str, content:str=Body(...), author:str=Body(...)):
    if not (posts.post_exists(post_id) or comment_exists(post_id)):
        raise HTTPException(status_code=404, detail="Post not found")
    comment_id = str(uuid.uuid4()) 
    comment = Comment(id=comment_id, content=content, author=author, parent_post_id=post_id)
    comments.append(comment)
    return comment

@router.get("/{post_id}", response_model=List[Comment], tags=["Comments"])
def read_comments(post_id: str):
    return [comment for comment in comments if comment.parent_post_id  == post_id]

@router.delete("/{comment_id}", tags=["Comments"])
def delete_comment(comment_id: str):
    global comments
    comments = [comment for comment in comments if comment.id != comment_id]
    return {"message": "Comment deleted successfully"}

@router.put("/{comment_id}", response_model=Comment, tags=["Comments"])
def update_comment(comment_id: str, content: str = Body(...)):
    comment = next((c for c in comments if c.id == comment_id), None)
    if comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    comment.content = content
    return comment

def comment_exists(comment_id):
    return any(comment.id == comment_id for comment in comments)