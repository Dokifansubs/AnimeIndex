from sqlalchemy import Column, Integer, BigInteger, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship, backref

from engine import Base
from user import User


class Category(Base):
    __tablename__ = 'category'
    __table_args__ = {'mysql_engine':'InnoDB'}

    id = Column(Integer, primary_key=True)
    index = Column(BigInteger)
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
    info = Column(String(1024))
    description = Column(Text)

    category = relationship("Category", backref=backref('torrents', order_by=id))
    user = relationship("User", backref=backref('torrents', order_by=id))

    def get_group(self):
        group = {"is": False, "name": None, "class": ""}
        if self.filename.find("]") > self.filename.find("[") and self.filename.find("[") == 0:
            group["is"] = True
            group["name"] = self.filename[1:self.filename.find("]")]
            if group["name"] == "Doki":
                group["class"] = "verified"
            elif group["name"] == "MNF":
                group["class"] = "unknown"

        return group

    @property
    def _id(self):
        return str(self.id)

    @property
    def status(self):
        return "S: 5 L: 2 C: 6"

    @property
    def size_friendly(self):
        return "%s Bytes" % self.size

    @property
    def age(self):
        return self.created.strftime("%H:%M")

    def __repr__(self):
        return "<Torrent('%s','%s', '%s')>" % (self.username, self.fullname, self.email)


class TorrentDateGroup(object):
    def __init__(self, date, torrent=None):
        self.date = date
        self.torrents = []
        if torrent != None:
            self.torrents.append(torrent)