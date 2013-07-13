from bottle import route, run, template, Bottle, static_file, install
from bottle.ext import sqlalchemy
from lesscss import LessCSS

from db import *
from common import render, default

LessCSS(media_dir='static', exclude_dirs=['img', 'src'], based=False, compressed=False)

@route('/static/<filename:path>')
def static(filename):
    return static_file(filename, root="static")

@route('/')
@default
def index(db):
    news = db.query(News).order_by(News.id.desc())[0:3]
    return render(news=news)

install(sqlalchemy.SQLAlchemyPlugin(engine, Base.metadata, create=True))
run(host='localhost', port=8080)