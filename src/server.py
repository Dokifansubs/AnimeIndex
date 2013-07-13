from bottle import route, run, template, Bottle, static_file
from bottle.ext import sqlalchemy
from lesscss import LessCSS

from db import *
from common import render

LessCSS(media_dir='static', exclude_dirs=['img', 'src'], compressed=False)

app = Bottle()
plugin = sqlalchemy.Plugin(
    engine, # SQLAlchemy engine created with create_engine function.
    Base.metadata, # SQLAlchemy metadata to autocreate tables.
    keyword='db', # Keyword used to inject session database in a route.
    create=True, # Autocreate tables if they don't exist.
    commit=True, # If it is true, plugin commit changes after route is executed.
    use_kwargs=False
)
app.install(plugin)

@route('/static/<filename:path>')
def static(filename):
    return static_file(filename, root="static")

@route('/')
def index():
    options = {"page_title": "Index"}
    return render()

run(host='localhost', port=8080)