import bcrypt
import re

from sqlalchemy import Column, Integer, String, DateTime, Boolean
from engine import Base

class User(Base):
    __tablename__ = 'user'
    __table_args__ = {'mysql_engine':'InnoDB'}

    id = Column(Integer, primary_key=True)
    level = Column(Integer)
    username = Column(String(64))
    password = Column(String(64))
    salt = Column(String(30))
    email = Column(String(64))
    verified = Column(Boolean())
    created = Column(DateTime())
    last_login = Column(DateTime())

    def __repr__(self):
        return "<User('%s','%s')>" % (self.username, self.email)

    @staticmethod
    def hash_password(username, password, salt):
        if salt != "":
            return bcrypt.hashpw("%s%s" % (username, password), salt)
        return ""

    @staticmethod
    def generate_hash():
        return bcrypt.gensalt()

    @staticmethod
    def valid_email(email):
        return not (email == "" or \
                    not re.match(r"[^@]+@[^@]+\.[^@]+", email))