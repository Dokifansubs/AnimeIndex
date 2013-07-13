from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship, backref

from engine import Base
from user import User

class News(Base):
    __tablename__ = 'news'
    __table_args__ = {'mysql_engine':'InnoDB'}

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))

    created = Column(DateTime())
    title = Column(String(100))
    content = Column(String(1024))

    user = relationship("User", backref=backref('news', order_by=id))

    def __repr__(self):
        return "<News('%s','%s', '%s')>" % (self.username, self.fullname, self.email)