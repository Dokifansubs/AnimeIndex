import bencode
import settings
import base64
import hashlib
import urllib

from sqlalchemy import Column, Integer, BigInteger, String, Text, DateTime, Binary, ForeignKey
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


class TStatus(Base):
    __tablename__ = 'xbt_files'
    __table_args__ = {'mysql_engine':'InnoDB'}

    info_hash = Column('info_hash', Binary(20), primary_key=True)
    seeders = Column('seeders', Integer)
    leechers = Column('leechers', Integer)
    completed = Column('completed', Integer)

    @property
    def _id(self):
        return str(self.info_hash)

class Magnet(Base):
    __tablename__ = 'magnet_links'
    __table_args__ = {'mysql_engine':'MyISAM'} #InnoDB

    id = Column(Integer, primary_key=True)
    info_hash = Column('info_hash', String(40), ForeignKey('xbtit_files.info_hash'))
    magnet = Column('magnet', String(254))

    torrent = relationship("Torrent", backref=backref('magnet', uselist=False))

    @property
    def _id(self):
        return str(self.info_hash)

class Torrent(Base):
    __tablename__ = 'xbtit_files'
    __table_args__ = {'mysql_engine':'InnoDB'}

    id = Column('info_hash', String(40), primary_key=True)
    category_id = Column('category', Integer, ForeignKey('xbtit_categories.id'))
    user_id = Column('uploader', Integer, ForeignKey('xbtit_users.id'))
    info_bin = Column('bin_hash', Binary(20), ForeignKey('xbt_files.info_hash'))

    created = Column('data', DateTime())
    filename = Column('filename', String(128))
    size = Column('size', BigInteger)
    info = Column('info', String(1024))
    description = Column('comment', Text)
    file_path = Column('url', Text)

    category = relationship("Category", backref=backref('torrents', order_by=id))
    user = relationship("User", backref=backref('torrents', order_by=id))
    status = relationship("TStatus", backref=backref('torrent', uselist=False))

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
    def friendly_status(self):
        return "%s / %s (%s)" % (self.status.seeders, self.status.leechers, self.status.completed)

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
        #return self.created
        #self.created.strftime("%H:%M")
        n = datetime.now()
        age = n - self.created
        if age.days < 2:
            return "%s Hours" % (age.days * 24 + age.seconds // 3600)
        else:
            return "%s Days" % age.days

    @property
    def is_recent(self):
        return (datetime.now() - self.created).days <= 6

    def generate_magnet(self, db):
        if self.magnet != None:
            return
        torrent = open(settings.TORRENT_HOME + "/" + self.file_path, 'r').read()
        metadata = bencode.bdecode(torrent)
        hashcontents = bencode.bencode(metadata['info'])
        digest = hashlib.sha1(hashcontents).digest()
        b32hash = base64.b32encode(digest)
        params = (('xt', 'urn:btih:%s' % b32hash),
                  ('tr', metadata['announce']),
                  ('dn', metadata['info']['name']))
        if metadata['info'].has_key('length'):
            params = params + (('xl', metadata['info']['length']),)
        paramstr = urllib.urlencode(params, True)
        magnet = Magnet(torrent=self,
                        magnet="magnet:?%s" % paramstr)
        db.add(magnet)
        self.magnet = magnet
        db.commit()

    def get_magnet(self):
        return self.magnet.magnet

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
