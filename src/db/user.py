from sqlalchemy import Column, Integer, String, DateTime

from engine import Base

class User(Base):
    __tablename__ = 'user'
    __table_args__ = {'mysql_engine':'InnoDB'}

    id = Column(Integer, primary_key=True)
    level = Column(Integer)
    username = Column(String(64))
    fullname = Column(String(64))
    password = Column(String(64))
    email = Column(String(64))
    created = Column(DateTime())
    last_login = Column(DateTime())

    def __init__(self, *args, **kwargs):
    	super(User, self).__init__(args, kwargs)

    def __repr__(self):
    	return "<User('%s','%s', '%s')>" % (self.username, self.fullname, self.email)