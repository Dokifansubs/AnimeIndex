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
