import bottle
from bottle import route, run, template, Bottle, static_file, install, request, error, debug
from bottle.ext import sqlalchemy
from lesscss import LessCSS
from beaker.middleware import SessionMiddleware

from db import *
from common import render, default
from views import *
import settings

LessCSS(media_dir='static', exclude_dirs=['img', 'src'], based=False, compressed=False)

@route('/static/<filename:path>')
def static(filename):
    return static_file(filename, root="static")

@route('/')
@default
def index(db):
    important_news = db.query(News).order_by(News.id.desc()).first()
    news = db.query(News).order_by(News.id.desc())[1:4]

    query = db.query(Torrent).join(Torrent.category)
    pager = paginator(query.order_by(Torrent.created.desc()), 1, 50)
    torrents = pager.items
    groups = []
    if len(torrents) > 0:
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
    for i in range(0, len(torrents)):
        torrents[i].generate_magnet(db)

    categories = db.query(Category).all()

    return render(news=news,
                  important_news=important_news,
                  torrent_group=groups,
                  sort="date",
                  pager=pager,
                  categories=categories)

@error(404)
@default
def error404(db, error):
    return render("message", message=[
        "The requested page or file was not found.",
        """If you're trying to open a torrent file, you either don't have permission
           to view it or the torrent in question got deleted."""])


"""
@error(500)
def error500(error):
    send_email("error",
               "%s - %s" % (settings.TITLE, error.status),
               settings.ADMIN,
               path=request.path,
               exception=error.exception,
               traceback=error.traceback)

    return render("message", message=[
        "An unknown error occured while processing your request.",
        "This error has been logged and our code monkeys will do \
         all in their power to fix this."])
"""


install(sqlalchemy.SQLAlchemyPlugin(engine, Base.metadata, create=True))

session_opts = {
    'session.type': 'file',
    'session.cookie_expires': 300,
    'session.data_dir': './data',
    'session.auto': True,
    'session.secret': settings.SESSION_KEY
}

app = bottle.default_app()
app = SessionMiddleware(app, session_opts)

run(app=app, host='localhost', reloader=True, port=8080)
