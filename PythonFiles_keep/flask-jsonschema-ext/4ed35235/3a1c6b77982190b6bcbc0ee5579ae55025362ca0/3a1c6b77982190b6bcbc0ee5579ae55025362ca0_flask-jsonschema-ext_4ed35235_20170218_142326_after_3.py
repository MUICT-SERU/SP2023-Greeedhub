from sqlalchemy import Column, Table, Integer, String, create_engine
from sqlalchemy import ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()
Session = sessionmaker()


class Post(Base):
    __jsonschema_include__ = ['post_value']
    __tablename__ = 'post'
    post_id = Column(Integer, primary_key=True)
    post_value = Column(String)
    author_id = Column(Integer, ForeignKey('author.author_id'))


class Author(Base):
    __jsonschema_exclude__ = ['author_id']
    __tablename__ = 'author'
    author_id = Column(Integer, primary_key=True)
    author_name = Column(String)

    posts = relationship(Post, backref='author')
