import datetime
from bottle import route, request, redirect, post
from common import render, default

from db import User, Torrent, Category, TorrentDateGroup
from mail_helper import send_email

@route('/torrent/')
@route('/torrent/<torrent_id:int>')
@default
def torrent_view(db, torrent_id=None):
    if torrent_id != None:
        pass
    page = request.query.get("page", 0)
    per_page = 50
    torrents = db.query(Torrent).order_by(Torrent.created.desc())[per_page*page:per_page+per_page*page]
    groups = []
    if len(torrents) > 0:
        groups.append(TorrentDateGroup(torrents[0].created.date(),
                                       torrents[1]))
        for i in range(1, len(torrents)):
            t = torrents[i]
            if t.created.date() == groups[-1].date:
                groups[-1].torrents.append(t)
            else:
                groups.append(TorrentDateGroup(t.created.date(), t))
    return render("torrent", torrent_group=groups)