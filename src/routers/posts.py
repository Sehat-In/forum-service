from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from typing import List
import uuid
from datetime import datetime

router = APIRouter(
    prefix="/posts",
    tags=["posts"],
    responses={404: {"description": "Not found"}},
)

class Post(BaseModel):
    id: str 
    title: str
    content: str
    author: str
    created_at: datetime = datetime.now()

posts = []


@router.post("/", response_model=Post, tags=["Posts"])
def create_post(title:str=Body(...), content:str=Body(...), author:str=Body(...)):
    post_id = str(uuid.uuid4())  
    post = Post(id=post_id, title=title, content=content, author=author)
    posts.append(post)
    return post
    
@router.get("/", response_model=List[Post], tags=["Posts"])
def read_posts():
    return posts

@router.get("/{post_id}", response_model=Post, tags=["Posts"])
def read_post(post_id: str):
    for post in posts:
        if post.id == post_id:
            return post
    raise HTTPException(status_code=404, detail="Post not found")

@router.delete("/{post_id}", tags=["Posts"])
def delete_post(post_id: str):
    global posts
    posts = [post for post in posts if post.id != post_id]
    return {"message": "Post deleted successfully"}

@router.put("/{post_id}", response_model=Post, tags=["Posts"])
def update_comment(post_id: str, title: str = Body(...), content: str = Body(...)):
    post = next((p for p in posts if p.id == post_id), None)
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    post.title = title
    post.content = content
    return post

def post_exists(post_id):
    return any(post.id == post_id for post in posts)