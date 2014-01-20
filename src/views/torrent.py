import datetime
from bottle import route, request, redirect, post
from common import render, default, paginator

from db import User, Torrent, Category, TStatus, TorrentDateGroup
from mail_helper import send_email

@route('/torrent/')
@route('/torrent/<torrent_id:int>')
@default
def torrent_view(db, torrent_id=None):
    title = "Torrents"

    if torrent_id != None:
        pass
    try:
        page = int(request.query.get("page", 1))
        if page < 1:
            page = 1
    except:
        page = 1
    try:
        per_page = int(request.query.get("per_page", 50))
    except:
        per_page = 50
    sort = request.query.get("sort", "")
    asc = sort[:1] == "+"
    if asc:
        sort = sort[1:]

    sorting = Torrent.created
    if sort == "size":
        sorting = Torrent.size
    elif sort == "name":
        sorting = Torrent.filename
    elif sort == "status":
        sorting = TStatus.seeders
    else:
        sorting = Torrent.created
        sort = "date"

    if asc:
        sorting = sorting.asc()
    else:
        sorting = sorting.desc()

    query = db.query(Torrent).join(Torrent.category)
    if sort == "status":
        query = query.join(Torrent.status)

    selected_cat = "all"

    if request.query.get("cat", "") != "" and request.query.get("cat", "").lower() != "all":
        query = query.filter(Category.name == request.query.get("cat"))
        title = request.query.get("cat") + " " + title
        selected_cat = request.query.get("cat")

    if request.query.get("q", "") != "":
        for x in request.query.get("q").split(" "):
            query = query.filter(Torrent.filename.like("%" + x + "%"))
        title = request.query.get("q") + " &laquo; " + title[:-1] + " Search"

    pager = paginator(query.order_by(sorting), page, per_page)

    torrents = pager.items
    groups = []
    if len(torrents) > 0 and sort == "date" and False:
        groups.append(TorrentDateGroup(torrents[0].created.date(),
                                       torrents[0]))
        for i in range(1, len(torrents)):
            t = torrents[i]
            if t.created.date() == groups[-1].date:
                groups[-1].torrents.append(t)
            else:
                groups.append(TorrentDateGroup(t.created.date(), t))
    else:
        groups = [TorrentDateGroup(torrents=torrents)]
    if asc:
        sort = "+" + sort

    for i in range(0, len(torrents)):
        torrents[i].generate_magnet(db)

    categories = db.query(Category).all()

    return render("torrent/torrent",
                  title,
                  torrent_group=groups,
                  sort=sort,
                  pager=pager,
                  categories=categories,
                  selected_cat=selected_cat,
                  searching=request.query.get("q", ""))
