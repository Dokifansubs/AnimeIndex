from bottle import route, request, redirect, abort, static_file
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound

import settings
from common import default

from db import Torrent

@route('/<filename:re:.*\.torrent>')
@route('/<filehash:re:[0-9a-fA-F]{40}>')
@default
def download(db, filename=None, filehash=None):
    print filename
    print filehash
    try:
        if filename != None:
            print filename[:-8]
            torrent = db.query(Torrent).filter(Torrent.filename.like(filename[:-8])).one()
        else:
            torrent = db.query(Torrent).filter(Torrent.id==filehash).one()
    except MultipleResultsFound, e:
        return render("message", message=["Multiple results were returned for this file name."])
    except NoResultFound, e:
        print e
        abort(404)
    print torrent.file_path
    return static_file(torrent.file_path, root=settings.TORRENT_HOME, download=torrent.filename + ".torrent", mimetype='application/x-bittorrent')
