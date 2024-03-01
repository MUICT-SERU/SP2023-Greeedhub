from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relation, sessionmaker

_Base = declarative_base()

class Article(_Base):
    __tablename__ = 'article'

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    sub_title = Column(String(255))

    main_author_id = Column(Integer, ForeignKey('author.id'))
    author = relation('Author', backref='articles')

    is_visible = Column(Boolean)


class Draft(_Base):
    __tablename__ = 'draft'

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    sub_title = Column(String(255))

    article_id = Column(Integer, ForeignKey('article.id'))
    article = relation('Article', backref='drafts')


class Author(_Base):
    __tablename__ = 'author'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    alias = Column(String(255))


class CoWrite(_Base):
    __tablename__ = 'co_write'

    id = Column(Integer, primary_key=True)

    article_id = Column(Integer, ForeignKey('article.id'))
    article = relation('Article', backref='co_writes')

    author_id = Column(Integer, ForeignKey('author.id'))
    author = relation('Author', backref='co_writes')
