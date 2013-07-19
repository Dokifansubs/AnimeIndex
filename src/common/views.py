import inspect
import functools

from bottle import request, redirect
from jadeview import template, view

import settings
from util import UtilClass
from db import User

def default(*args, **kwargs):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(db, *args, **kwargs):
            logged_in_user = request.environ.get('beaker.session').get("_user", None)
            if logged_in_user != None:
                logged_in_user = db.query(User).filter_by(username=logged_in_user).first()
                request.environ["_logged_in_user"] = logged_in_user

            if db not in args:
                args = (db,) + args



            if request.method == "POST" and not UtilClass.is_csrf_correct():
                request.environ["_form_errors"] = ["CSRF is incorrect. Please try again."]
                if on_error != None:
                    if "user" in inspect.getargspec(on_error)[0] and "user" not in kwargs and logged_in_user not in args:
                        kwargs["user"] = logged_in_user
                    return on_error(*args, **kwargs)

            if has_captcha and not UtilClass.verify_captcha():
                request.environ["_form_errors"] = ["Captcha was incorrect. Please try again."]
                if on_error != None:
                    if "user" in inspect.getargspec(on_error)[0] and "user" not in kwargs and logged_in_user not in args:
                        kwargs["user"] = logged_in_user
                    return on_error(*args, **kwargs)

            if "user" in inspect.getargspec(func)[0] and "user" not in kwargs and logged_in_user not in args:
                kwargs["user"] = logged_in_user

            return func(*args, **kwargs)
        return wrapper

    if len(args) == 1 and callable(args[0]):
        on_error = None
        has_captcha = False
        return decorator(args[0])
    else:
        on_error = kwargs.get("on_error", None)
        has_captcha = kwargs.get("captcha", False)
        return decorator

def render(template_file="index", title="Index", **kwargs):
    template_file = "static/templates/%s" % template_file
    kwargs["util"] = UtilClass()
    kwargs["current_user"] = request.environ.get('_logged_in_user', None)
    kwargs["page_title"] = "%s &laquo; %s" % (title, settings.TITLE)
    kwargs["form_errors"] = kwargs.get("form_errors", []) + request.environ.get("_form_errors", [])
    kwargs["form_data"] = dict(kwargs.get("form_data", {}), **request.forms)
    return template(template_file, kwargs)