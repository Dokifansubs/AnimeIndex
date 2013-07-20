import hashlib
import re
import bcrypt
import datetime
from bottle import route, request, redirect, post
from common import render, default

from db import User
from mail_helper import send_email

@route('/profile/')
@default
def profile(db, user):
    if user == None:
        return profile_login_view(db)
    return render("profile")


@post('/profile/')
@default
def profile_submit(db, user):
    if user == None:
        return profile_login_view(db)

    request.environ["_form_errors"] = []

    if request.forms.get("password", "") != request.forms.get("password2", "") and \
            request.forms.get("password2", "") != "":
        request.environ["_form_errors"].append("Password don't match.")

    if request.forms.get("email", "") == "" or \
            not re.match(r"[^@]+@[^@]+\.[^@]+", request.forms.get("email", "")):
        request.environ["_form_errors"].append("Email must be a valid address.")
    elif db.query(User).filter_by(email=request.forms.get("email")).first() != user:
        request.environ["_form_errors"].append("Email is already taken.")
    print db.query(User).filter_by(email=request.forms.get("email")).first()
    print user
    if request.forms.get("current_password", "") == "" or \
            (user.password != user.hash_password(user.username.lower(),
                                                 request.forms.get("current_password"),
                                                 user.salt) and \
             user.password != hashlib.md5(request.forms.get("current_password")).hexdigest()):
        request.environ["_form_errors"].append("Password was wrong. Please try again.")

    if len(request.environ["_form_errors"]) > 0:
        return profile(db, user)

    if request.forms.get("password2", "") != "":
        user.salt = User.generate_hash()
        user.password = user.hash_password(user.username.lower(),
                                           request.forms.get("password2"),
                                           user.salt)
    user.email = request.forms.get("email")
    db.commit()
    redirect("/profile/")



@route('/profile/activate/<user_id:int>/<activation_link:path>')
@default
def activate_account(db, user_id, activation_link):
    user = db.query(User).filter_by(id=user_id).first()
    if user == None:
        return render("message", message=[
            """There was an unknown error while activating your account, please
               try again.""",
            """If the problem persist, please let us know on admin@anime-index.org
               so we can take a look at it."""])
    elif User.hash_password(user.username, "", user.salt) != activation_link:
        return render("message", message=[
            """There was an unknown error while activating your account, please
               try again.""",
            """If the problem persist, please let us know on admin@anime-index.org
               so we can take a look at it."""])
    elif user.verified:
        return render("message", message=[
            """This account has already been activated.""",
            """If you're experiencing any problems with your account,
               please let us know on admin@anime-index.org
               so we can take a look at it."""])
    user.verified = True
    s = request.environ.get("beaker.session")
    s["_user"] = user.username
    s.save()
    db.commit()
    request.environ["_logged_in_user"] = user

    return render("message", message=[
            """Congratualations, your account was activated successfully and
               you are now logged in.""",
            """If you're experiencing any problems with your account,
               please let us know on admin@anime-index.org
               so we can take a look at it."""])


@route('/profile/recover/<user_id:int>/<reset_link:path>')
@default
def recover_reset_view(db, user_id, reset_link):
    user = db.query(User).filter_by(id=user_id).first()
    if user == None:
        return render("message", message=[
            """There was an unknown error while attempting to reset your account.""",
            """If the problem persist, please let us know on admin@anime-index.org
               so we can take a look at it."""])
    elif User.hash_password(user.username, user.password, user.salt) != reset_link:
        return render("message", message=[
            """There was an unknown error while attempting to reset your account.""",
            """If the problem persist, please let us know on admin@anime-index.org
               so we can take a look at it."""])
    return render("reset")


@post('/profile/recover/<user_id:int>/<reset_link:path>')
@default
def recover_reset_submit(db, user_id, reset_link):
    request.environ["_form_errors"] = []
    user = db.query(User).filter_by(id=user_id).first()
    if user == None:
        return render("message", message=[
            """There was an unknown error while attempting to reset your account.""",
            """If the problem persist, please let us know on admin@anime-index.org
               so we can take a look at it."""])
    elif User.hash_password(user.username, user.password, user.salt) != reset_link:
        return render("message", message=[
            """There was an unknown error while attempting to reset your account.""",
            """If the problem persist, please let us know on admin@anime-index.org
               so we can take a look at it."""])

    if request.forms.get("password", "") != request.forms.get("password2", ""):
        request.environ["_form_errors"].append("Password don't match.")
    elif request.forms.get("password", "") == "":
        request.environ["_form_errors"].append("Please type a valid password.")

    if len(request.environ["_form_errors"]) > 0:
        return recover_reset_view(db, user_id, reset_link)

    user.salt = User.generate_hash()
    user.password = User.hash_password(user.username.lower(),
                       request.forms.get("password"),
                       user.salt)
    db.commit()
    request.environ["_logged_in_user"] = user
    s = request.environ.get("beaker.session")
    s["_user"] = user.username
    s.save()

    return render("message", message=["""Your password has been successfully reset."""])


@route('/profile/recover')
@default
def recover_view(db):
    return render("recover")


@post('/profile/recover')
@default
def recover_submit(db):
    user = db.query(User).filter_by(email=request.forms.get("email", "")).first()
    if user != None:
        send_email("recover",
                   "Anime Index - Reset Password",
                   user.email,
                   username=user.username,
                   id=user.id,
                   reset=User.hash_password(
                        user.username,
                        user.password,
                        user.salt
                   ))
    return render("message", message=[
        "A password reset email has been sent to the address specified.",
        """If you're not receiving any email, please contact the 
           admin on admin@anime-index.org."""])


@route('/profile/registered')
@default
def registered_view(db):
    return render("message", message=[
        "Thank you for registering on Anime Index.",
        """An activation email has been sent to the email address specified,
           which needs to be activated before your account is fully open.""",
        """We welcome any feedback on what you think, so please don't hesitate
           contact the admin on admin@anime-index.org."""])


@route('/profile/register')
@default
def register_view(db):
    return render("register", form_data=request.forms)


@post('/profile/register')
@default
def register_submit(db):
    request.environ["_form_errors"] = []
    username = request.forms.get("username", "")
    if request.forms.get("password", "") != request.forms.get("password2", ""):
        request.environ["_form_errors"].append("Password don't match.")
    elif request.forms.get("password", "") == "":
        request.environ["_form_errors"].append("Please type a valid password.")
    if request.forms.get("email", "") != request.forms.get("email2", ""):
        request.environ["_form_errors"].append("Email doesn't match.")
    elif request.forms.get("email", "") == "" or \
            not re.match(r"[^@]+@[^@]+\.[^@]+", request.forms.get("email", "")):
        request.environ["_form_errors"].append("Email must be a valid address.")
    elif db.query(User).filter_by(email=request.forms.get("email")).first() != None:
        request.environ["_form_errors"].append("""Email is already taken
            (<a href="/profile/recover">forgot your password?</a>).
            """)
    if db.query(User).filter_by(username=username).first() != None:
        request.environ["_form_errors"].append("Username is already taken.")
    elif username == "":
        request.environ["_form_errors"].append("Please type in a username.")

    if len(request.environ["_form_errors"]) > 0:
        return register_view(db)

    salt = User.generate_hash()
    user = User(username=request.forms.get("username"),
                level=1,
                password=User.hash_password(request.forms.get("username").lower(),
                                            request.forms.get("password"),
                                            salt),
                salt=salt,
                email=request.forms.get("email"),
                verified=False,
                created=datetime.datetime.now())
    db.add(user)
    db.commit()

    send_email("activation",
               "Anime Index - Activate your account",
               user.email,
               username=user.username,
               id=user.id,
               activation=User.hash_password(
                    user.username,
                    "",
                    user.salt
               ))

    redirect("/profile/registered")


@route('/profile/login')
@default
def profile_login_view(db):
    return render("login")


@post('/profile/login')
@default
def profile_login_submit(db):
    username = request.forms.get("username", "")
    password = request.forms.get("password", "")

    user = db.query(User).filter_by(username=username, verified=True).first()
    if user == None:
        user = db.query(User).filter_by(email=username, verified=True).first()

    if user != None and \
            (user.password == user.hash_password(user.username.lower(), password, user.salt) or \
             user.password == hashlib.md5(password).hexdigest()):
        s = request.environ.get("beaker.session")
        s["_user"] = user.username
        s.save()
        redirect("/")
    
    request.environ["_form_errors"] = ["Username or password was incorrect."]
    return profile_login_view(db)


@route('/profile/logout')
@default
def profile_logout(db):
    s = request.environ.get("beaker.session")
    try:
        del s["_user"]
    finally:
        redirect("/")