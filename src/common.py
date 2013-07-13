from jadeview import template, view

import settings

def render(template_file="static/templates/index", title="Index", **kwargs):
	kwargs['page_title'] = "%s &laquo; %s" % (title, settings.TITLE)
	return template(template_file, kwargs)