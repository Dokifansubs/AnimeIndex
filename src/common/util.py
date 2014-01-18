import urllib

from recaptcha.client import captcha
from bottle import request

from pprint import pprint

import settings

class UtilClass(object):

    @staticmethod
    def generate_csrf():
        s = request.environ.get('beaker.session')
        if not s.has_key("_csrf_token"):
            import string
            import random

            symbols = string.ascii_lowercase + string.ascii_uppercase + string.digits
            s["_csrf_token"] = "".join(random.choice(symbols) for x in range(28))
            s.save()
        return s["_csrf_token"]

    @staticmethod
    def link(input, remove_page=False):
        if remove_page:
            request.query.pop('page', None)
        path = request.path + "?"
        query = dict(request.query.items() + input.items()).items()
        path += "&".join(x[0] + "=" + urllib.quote(x[1], '') for x in query)
        return path

    @staticmethod
    def is_csrf_correct():
        csrf = request.forms.get("csrf", "")
        s = request.environ.get('beaker.session')
        if s.get("_csrf_token", "") != csrf or csrf == "":
            return False
        return True

    @staticmethod
    def display_captcha():
        if request.environ.get('_logged_in_user', None) != None:
            return ""
        return captcha.displayhtml(settings.CAPTCHA_PUBLIC_KEY)

    @staticmethod
    def verify_captcha():
        if request.environ.get('_logged_in_user', None) != None:
            return True
        challenge = request.forms.get("recaptcha_challenge_field", "")
        response = request.forms.get("recaptcha_response_field", "")
        if challenge != "" or response != "":
            return captcha.submit(challenge, response, settings.CAPTCHA_PRIVATE_KEY,
                request.remote_addr).is_valid
        return False