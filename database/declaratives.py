import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class Board(Base):
    __tablename__ = 'board'
    __classname__ = 'Board'
    name = Column(String(150), nullable=False)
    location = Column(String(200))
    unique_name = Column(String(100), nullable=False, primary_key=True)
    update_time = Column(Integer, nullable=False)
    posts = relationship("Post", back_populates="group")

class Post(Base):
    __tablename__ = 'post'
    __classname__ = 'Post'
    id = Column(Integer, primary_key=True)
    post_type = Column(String(7), nullable=False)
    date = Column(Integer, nullable=False)
    name = Column(String(150), nullable=False)
    location = Column(String(150), nullable=False)
    update_time = Column(Integer, nullable=False)
    group_name = Column(String(100), ForeignKey('board.unique_name'))
    group = relationship("Board", back_populates="posts")

    def __str__(self):
        return '{} in {}'.format(self.name, self.group_name)
    
    def __repr__(self):
        return '{} in {}'.format(self.name, self.group_name)

# Create an engine that stores data in the local directory's
# sqlalchemy_example.db file.
engine = create_engine('sqlite:///freecycle.db')

# Create all tables in the engine. This is equivalent to "Create Table"
# statements in raw SQL.
Base.metadata.create_all(engine)