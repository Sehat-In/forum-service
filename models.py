from datetime import datetime
import uuid
from database import Base
from sqlalchemy import Column, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID


class BaseModel(Base):
    __abstract__ = True
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

class Post(BaseModel):
    __tablename__ = 'posts'
    
    title = Column(String, index=True)
    content = Column(String)
    username = Column(String)
    created_at = Column(DateTime, default=datetime.now)

    # Relationship with comments
    comments = relationship("Comment", back_populates="post", cascade="all, delete")
    likes = relationship('Like', back_populates='post', cascade="all, delete")
    subscribes = relationship('Subscribe', back_populates='post', cascade="all, delete")

class Comment(BaseModel):
    __tablename__ = 'comments'
    
    content = Column(String)
    username = Column(String)
    created_at = Column(DateTime, default=datetime.now)

    # Relationship with post
    parent_post_id = Column(UUID(as_uuid=True), ForeignKey('posts.id'))
    post = relationship("Post", back_populates="comments")
    
    # Self-referential relationship for replies
    parent_comment_id = Column(UUID(as_uuid=True), ForeignKey('comments.id'))
    children = relationship("Comment", backref="parent_comment", remote_side="[Comment.id]")

    likes = relationship('Like', back_populates='comment', cascade="all, delete")


class Like(BaseModel):
    __tablename__ = 'likes'

    username = Column(String)

    # Relationship with post
    post_id = Column(UUID(as_uuid=True), ForeignKey('posts.id'))
    post = relationship('Post', back_populates='likes')
    
    # Relationship with comment
    comment_id = Column(UUID(as_uuid=True), ForeignKey('comments.id'))
    comment = relationship('Comment', back_populates='likes')

    __table_args__ = (
        UniqueConstraint('username', 'post_id', name='_username_post_uc'),
        UniqueConstraint('username', 'comment_id', name='_username_comment_uc')
    )

class Subscribe(BaseModel):
    __tablename__ = 'subscribes'

    username = Column(String)

    # Relationship with post
    post_id = Column(UUID(as_uuid=True), ForeignKey('posts.id'))
    post = relationship('Post', back_populates='subscribes')

    created_at = Column(DateTime, default=datetime.now)

    __table_args__ = (
        UniqueConstraint('username', 'post_id', name='_username_subscribes_uc'),
    )