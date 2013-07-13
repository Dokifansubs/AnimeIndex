from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship, backref

from engine import Base
from user import User

class Category(Base):
    __tablename__ = 'category'
    __table_args__ = {'mysql_engine':'InnoDB'}

    id = Column(Integer, primary_key=True)
    index = Column(Integer)
    name = Column(String(128))
    image = Column(String(128))

    def __repr__(self):
        return "<Category('%s','%s', '%s')>" % (self.username, self.fullname, self.email)

class Torrent(Base):
    __tablename__ = 'torrent'
    __table_args__ = {'mysql_engine':'InnoDB'}

    id = Column(Integer, primary_key=True)
    category_id = Column(Integer, ForeignKey('category.id'))
    user_id = Column(Integer, ForeignKey('user.id'))

    created = Column(DateTime())
    info_hash = Column(String(50))
    filename = Column(String(128))
    size = Column(Integer)
    info = Column(String(100))
    description = Column(String(1024))

    category = relationship("Category", backref=backref('torrents', order_by=id))
    user = relationship("User", backref=backref('torrents', order_by=id))

    def __repr__(self):
        return "<Torrent('%s','%s', '%s')>" % (self.username, self.fullname, self.email)