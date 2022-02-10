from . import app
from .models import User
from flask import render_template, request, redirect, url_for, session, flash
import functools

from werkzeug.security import check_password_hash, generate_password_hash

from pony.orm import db_session


def prihlasit(function):
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        if "user" in session:
            return function(*args, **kwargs)
        else:
            return redirect(url_for("login", url=request.path))

    return wrapper


@app.route("/", methods=["GET"])
@db_session
def index():
    temp = []
    for user in User.select():
        temp.append([user.nick, user.passwd])
    return render_template("base.html.j2", temp=temp)


@app.route("/add/", methods=["GET"])
def add():
    return render_template("add.html.j2")


@app.route("/add/", methods=["POST"])
@db_session
def add_post():
    nick = request.form.get("nick")
    passwd1 = request.form.get("passwd1")
    passwd2 = request.form.get("passwd2")

    if not all([nick, passwd1, passwd2]):
        flash("Musíš vyplnit všechna políčka", "error")
    else:
        user = User.get(nick=nick)
        if user:
            flash("Tento uživatel již existuje", "error")
        elif passwd1 != passwd2:
            flash("Hesla nejsou stejná", "error")
        else:
            user = User(nick=nick, passwd=generate_password_hash(passwd1))
            flash("Uživatel úspěšně vytvořen!", "success")
            session["nick"] = nick

    return redirect(url_for("add"))


@app.route("/login/")
def login():
    return render_template("login.html.j2")


@app.route("/login/", methods=["POST"])
@db_session
def login_post():
    nick = request.form.get("nick")
    passwd = request.form.get("passwd")

    if all([nick, passwd]):
        user = User.get(nick=nick)
        if user and check_password_hash(user.passwd, passwd):
            session["nick"] = nick
            flash("Jsi přihlášen!", "success")
            return redirect(url_for("index"))
        else:
            flash("Špatné přihlašovací údaje!", "error")
    else:
        flash("Zadej přihlašovací údaje!", "error")
    return redirect(url_for("login"))


@app.route("/logout/")
def logout():
    session.pop("nick", None)
    return redirect(url_for("index"))


@app.route("/text/")
def text():
    return """

<h1>Text</h1>

<p>toto je text</p>

"""
