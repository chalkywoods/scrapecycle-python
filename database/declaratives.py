import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class Board(Base):
    __tablename__ = 'board'
    name = Column(String(150), nullable=False)
    location = Column(String(200))
    unique_name = Column(String(100), nullable=False, primary_key=True)
    update_time = Column(Integer, nullable=False)

class Post(Base):
    __tablename__ = 'post'
    id = Column(Integer, primary_key=True)
    post_type = Column(String(7), nullable=False)
    date = Column(Integer, nullable=False)
    name = Column(String(150), nullable=False)
    location = Column(String(150), nullable=False)
    board_name = Column(String(100), ForeignKey('board.unique_name'))
    board = relationship(Board)

# Create an engine that stores data in the local directory's
# sqlalchemy_example.db file.
engine = create_engine('sqlite:///freecycle.db')

# Create all tables in the engine. This is equivalent to "Create Table"
# statements in raw SQL.
Base.metadata.create_all(engine)