from sqlalchemy import Column, Integer, BigInteger, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.hybrid import hybrid_property

from datetime import datetime
from engine import Base
from user import User


class Category(Base):
    __tablename__ = 'xbtit_categories'
    __table_args__ = {'mysql_engine':'InnoDB'}

    id = Column(Integer, primary_key=True)
    index = Column('sort_index', BigInteger)
    sub = Column('sub', Integer)
    name = Column(String(128))
    image = Column(String(128))

    def __repr__(self):
        return "<Category('%s','%s', '%s')>" % (self.username, self.fullname, self.email)


class Torrent(Base):
    __tablename__ = 'xbtit_files'
    __table_args__ = {'mysql_engine':'InnoDB'}

    id = Column('info_hash', String(40), primary_key=True)
    category_id = Column('category', Integer, ForeignKey('xbtit_categories.id'))
    user_id = Column('uploader', Integer, ForeignKey('xbtit_users.id'))

    created = Column('data', DateTime())
    filename = Column('filename', String(128))
    size = Column('size', BigInteger)
    info = Column('info', String(1024))
    description = Column('comment', Text)

    category = relationship("Category", backref=backref('torrents', order_by=id))
    user = relationship("User", backref=backref('torrents', order_by=id))

    def get_group(self):
        group = {"is": False, "name": None, "class": ""}
        if self.filename.find("]") > self.filename.find("[") and self.filename.find("[") >= 0:
            group["name"] = self.filename[1:self.filename.find("]")]
            #if group["name"] == "Doki":
            #    group["is"] = True
            #    group["class"] = "verified"
            #elif group["name"] == "MNF":
            #    group["class"] = "unknown"

        return group

    @hybrid_property
    def safe_name(self):
        return self.filename.decode('utf8').replace('&amp;', '&')

    @property
    def _id(self):
        return str(self.id)

    @property
    def status(self):
        return "S: 5 L: 2 C: 6"

    @property
    def size_friendly(self):
        num = self.size
        for x in ['bytes','KB','MB','GB']:
            if num < 1024.0:
                return "%3.1f %s" % (num, x)
            num /= 1024.0
        return "%3.1f %s" % (num, 'TB')

    @property
    def age(self):
        return self.created.strftime("%H:%M")

    @property
    def is_recent(self):
        return (datetime.now() - self.created).days < 2

    def __repr__(self):
        return "<Torrent('%s','%s', '%s')>" % (self.username, self.fullname, self.email)


class TorrentDateGroup(object):
    def __init__(self, date=None, torrent=None, torrents=None):
        self.date = date
        self.torrents = []
        if torrents != None:
            self.torrents = torrents
        if torrent != None:
            self.torrents.append(torrent)
