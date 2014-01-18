import bcrypt
import re

from sqlalchemy import Column, Integer, String, DateTime, Boolean
from engine import Base

class User(Base):
    __tablename__ = 'xbtit_users'
    __table_args__ = {'mysql_engine':'InnoDB'}

    id = Column(Integer, primary_key=True)
    level = Column('id_level', Integer)
    username = Column(String(64))
    password = Column(String(64))
    salt = Column(String(30))
    email = Column(String(64))
    verified = True
    #verified = Column('pass_type', Boolean())
    created = Column('joined', DateTime())
    last_login = Column('lastconnect', DateTime())

    def __repr__(self):
        return "<User('%s','%s')>" % (self.username, self.email)

    @property
    def _id(self):
        return str(self.id)

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