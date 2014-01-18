import hashlib

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship, backref

from engine import Base
from user import User

class News(Base):
    __tablename__ = 'news'
    __table_args__ = {'mysql_engine':'InnoDB'}

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('xbtit_users.id'))

    created = Column(DateTime())
    title = Column(String(100))
    content = Column(String(1024))

    user = relationship("User", backref=backref('news', order_by=id))

    @property
    def _id(self):
        return str(self.id)

    def __repr__(self):
        return "<News('%s')>" % (self.title)

class NewsComment(Base):
    __tablename__ = 'news_comments'
    __table_args__ = {'mysql_engine':'InnoDB'}

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('xbtit_users.id'))
    news_id = Column(Integer, ForeignKey('news.id'))

    username = Column(String(64))
    email = Column(String(64))
    url = Column(String(128))
    created = Column(DateTime())
    content = Column(String(1024))

    news = relationship("News", backref=backref('comments', order_by=id))
    user = relationship("User", backref=backref('news_comments', order_by=id))

    
    @property
    def get_url(self):
        if self.url[0:7] != "http://":
            return "http://%s" % self.url
        return self.url

    @property
    def author_img(self):
        email_post = self.email if self.user == None else self.user.email
        return "http://www.gravatar.com/avatar/%s?s=50&d=mm" % hashlib.md5(
                email_post.lower().strip()
            ).hexdigest()


    def __repr__(self):
        return "<NewsComment('%s', '%s', '%s')>" % (self.news.title,
                                                    self.created,
                                                    self.user)