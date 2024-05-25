from http.client import HTTPResponse
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
import pika
from fastapi import Response

load_dotenv()

router = APIRouter(
    prefix="/api/v1/posts",
    tags=["posts"],
    responses={404: {"description": "Not found"}},
)

@router.post("/create", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_post(post: schemas.PostCreate, db = Depends(get_db)):
    db_post = models.Post(title=post.title, content=post.content, username=post.username)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)

    db_subscribe = models.Subscribe(username=post.username, post_id=db_post.id)
    db.add(db_subscribe)
    db.commit()
    db.refresh(db_subscribe)
    
    add_notification_system(db_post)
    add_user_to_notification_system(db_post, post.username)
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
    delete_exchange(post_id)
    return Response(status_code=200, content="Post deleted")

@router.put("/update/{post_id}", response_model=schemas.Post)
def update_post(post_id: UUID, post: schemas.PostUpdate, db = Depends(get_db)):
    db_post = post_exists(post_id, db)
    db_post.title = post.title
    db_post.content = post.content
    db.commit()
    db.refresh(db_post)
    return db_post

@router.post("/subscribe", response_model=schemas.Subscribe)
def subscribe_to_post(subscribe: schemas.SubscribeCreate, db = Depends(get_db)):
    db_post = post_exists(subscribe.post_id, db)
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    db_subscribe = models.Subscribe(username=subscribe.username, post_id=subscribe.post_id)
    db.add(db_subscribe)
    db.commit()
    db.refresh(db_subscribe)
    add_user_to_notification_system(db_post, subscribe.username)
    return db_subscribe

@router.get("/check-notification/{username}")
def check_notification(username: str):
    return check_user_notification(username)

@router.get("/get-notifications/{username}")
def get_notifications(username: str):
    return get_user_notifications(username)

@router.delete("/unsubscribe")
def unsubscribe(subscribe: schemas.SubscribeCreate, db = Depends(get_db)):
    db_subscribe = unsubscribe_from_post(subscribe.username, subscribe.post_id, db)
    if db_subscribe is None:
        raise HTTPException(status_code=404, detail="Subscription not found")
    unbind_exchange(subscribe.username, subscribe.post_id)
    return Response(status_code=200, content="Unsubscribed")

@router.get("/get-subscriptions/{username}", response_model=List[schemas.Subscribe])
def get_subscriptions(username: str, db = Depends(get_db)):
    return db.query(models.Subscribe).filter(models.Subscribe.username == username).all()

def post_exists(post_id: UUID, db: Session):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    return post

def add_notification_system(db_post: models.Post):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=os.getenv('RABBITMQ_SERVER'), credentials=pika.PlainCredentials(os.getenv('RABBITMQ_USERNAME'), os.getenv('RABBITMQ_PASSWORD'))))
    channel = connection.channel()
    channel.exchange_declare(exchange=f'notification_{db_post.id}', exchange_type='fanout')
    connection.close()

def add_user_to_notification_system(db_post: models.Post, username: str):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=os.getenv('RABBITMQ_SERVER'), credentials=pika.PlainCredentials(os.getenv('RABBITMQ_USERNAME'), os.getenv('RABBITMQ_PASSWORD'))))
    channel = connection.channel()
    channel.queue_declare(queue=f'notification_{username}')
    channel.queue_bind(exchange=f'notification_{db_post.id}', queue=f'notification_{username}')
    connection.close()

def check_user_notification(username: str):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=os.getenv('RABBITMQ_SERVER'), credentials=pika.PlainCredentials(os.getenv('RABBITMQ_USERNAME'), os.getenv('RABBITMQ_PASSWORD'))))
    channel = connection.channel()
    method_frame, _, _ = channel.basic_get(queue=f'notification_{username}')
    connection.close()
    if method_frame:
        return Response(status_code=200, content="You have notification!")
    raise HTTPException(status_code=404, detail="No notification")

def get_user_notifications(username: str):
    messages = []
    def callback(ch, method, properties, body):
        messages.append(body)   
        if (len(messages) == message_count):
            ch.stop_consuming()
    
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=os.getenv('RABBITMQ_SERVER'), credentials=pika.PlainCredentials(os.getenv('RABBITMQ_USERNAME'), os.getenv('RABBITMQ_PASSWORD'))))
    channel = connection.channel()
    message_count = channel.queue_declare(queue=f'notification_{username}', passive=True).method.message_count
    channel.basic_consume(queue=f'notification_{username}', on_message_callback=callback)
    try:
        channel.start_consuming()
    except pika.exceptions.ConsumerCancelled:
        pass
    connection.close()

    return messages

def unsubscribe_from_post(username:str, post_id:UUID, db: Session):
    db_subscribe = db.query(models.Subscribe).filter(models.Subscribe.username == username, models.Subscribe.post_id == post_id).first()
    db.delete(db_subscribe)
    db.commit()
    return db_subscribe

def unbind_exchange(username: str, post_id: UUID):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=os.getenv('RABBITMQ_SERVER'), credentials=pika.PlainCredentials(os.getenv('RABBITMQ_USERNAME'), os.getenv('RABBITMQ_PASSWORD'))))
    channel = connection.channel()
    channel.queue_unbind(queue=f'notification_{username}', exchange=f'notification_{post_id}')
    connection.close()

def delete_exchange(post_id: UUID):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=os.getenv('RABBITMQ_SERVER'), credentials=pika.PlainCredentials(os.getenv('RABBITMQ_USERNAME'), os.getenv('RABBITMQ_PASSWORD'))))
    channel = connection.channel()
    channel.exchange_delete(exchange=f'notification_{post_id}')
    connection.close()