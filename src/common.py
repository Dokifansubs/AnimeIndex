import functools

from jadeview import template, view

import settings

def default(*args, **kwargs):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(db, *args, **kwargs):
            args = (db,) + args
            return func(*args, **kwargs)
        return wrapper

    if len(args) == 1 and callable(args[0]):
        # Set default values
        return decorator(args[0])
    else:
        # Save values from args
        return decorator

def render(template_file="static/templates/index", title="Index", **kwargs):
    kwargs['page_title'] = "%s &laquo; %s" % (title, settings.TITLE)
    return template(template_file, kwargs)

