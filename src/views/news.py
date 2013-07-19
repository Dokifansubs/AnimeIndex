import datetime

from bottle import route, post, request, redirect
from common import render, default, UtilClass

from db import News, NewsComment, User

@route('/news/')
@route('/news/<news_id:int>')
@default
def news_view(db, news_id=None):
    data = {}
    if news_id == None:
        data['news'] = db.query(News).order_by(News.id.desc())
        comments = []
    else:
        data['news'] = db.query(News).filter_by(id=news_id)
        data['comments_count'] = data['news'].count()
        data['comments_text'] = "Comment%s" % ("" if data['comments_count'] == 1 \
                                                else "s")
    data['show_comments'] = news_id != None
    return render("news", **data)

@post('/news/<news_id:int>')
@default(on_error=news_view, captcha=True)
def news_post(db, user, news_id):
    news = db.query(News).filter_by(id=news_id).first()

    if request.forms.get("content", "") == "":
        request.environ["_form_errors"] = ["Please type a message before hitting submit."]
        return news_view(db, news_id)
    if user == None:
        if not User.valid_email(request.forms.get("email", "")):
            request.environ["_form_errors"] = ["Please type a email address."]
            return news_view(db, news_id)
        if request.forms.get("name", "") == "":
            request.environ["_form_errors"] = ["Please type a name."]
            return news_view(db, news_id)
        n = NewsComment(username=request.forms.get("name"),
                        email=request.forms.get("email"),
                        url=request.forms.get("url", ""),
                        created=datetime.datetime.now(),
                        news=news,
                        content=request.forms.get("content", ""))
    else:
        n = NewsComment(user=user,
                        created=datetime.datetime.now(),
                        news=news,
                        content=request.forms.get("content"))

    db.add(n)
    db.commit()

    redirect(request.path)