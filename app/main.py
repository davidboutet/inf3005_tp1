from flask import Flask, request, render_template, redirect, g, flash, \
                  Response, session, jsonify
import hashlib
import uuid
import logging
import smtplib
import urllib
import re
from database import Database
from logging.handlers import RotatingFileHandler
from article import Article
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from functools import wraps

app = Flask(__name__, static_url_path="", static_folder="static")
app.secret_key = 'secretKey'
app.config.from_pyfile('config.cfg')


def is_authenticated(session):
    return "id" in session


def send_unauthorized():
    return render_template('/errors/401.html'), 401


def authentication_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not is_authenticated(session):
            return send_unauthorized()
        return f(*args, **kwargs)
    return decorated


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


# get login user
def get_user():
    username = None
    if "id" in session:
        username = Database().get_session(session["id"])
    return username


# send email
def send_email(email, subject="No subject", html=""):
    source_address = app.config["EMAIL"]
    destination_address = email

    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = source_address
    msg['To'] = destination_address

    msg.attach(MIMEText(html, 'html'))

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(source_address, app.config["PASSWORD"])
    text = msg.as_string()
    server.sendmail(source_address, destination_address, text)
    server.quit()


@app.route('/login', methods=["GET", "POST"])
def log_user():
    username = get_user()
    if request.method == "GET":
        return render_template("login.html", username=username)
    else:
        username = request.form["username"]
        password = request.form["password"]
        # Verifier que les champs ne sont pas vides
        if username == "" or password == "":
            return redirect("/login")

        user = Database().get_user_login_info(username)
        if user is None:
            message = {"status": "danger", "message": "Username or"
                                                      " password incorrect"}
            flash(message)
            return redirect("/login")

        salt = user[0]
        hashed_password = hashlib.sha512(password + salt).hexdigest()
        if hashed_password == user[1]:
            # Acces autorise
            id_session = uuid.uuid4().hex
            Database().save_session(id_session, username)
            session["id"] = id_session
            return redirect("/")
        else:
            return redirect("/login")


@app.route('/logout')
@authentication_required
def logout():
    if get_user():
        session.pop('id', None)
        Database().delete_session(get_user())
    return redirect("/")


@app.route("/", methods=["GET", "POST"])
def index():
    articles = Article()
    if request.method == "POST" and request.form["search_string"]:
        query_string = request.form["search_string"]
        articles = articles.search(query_string)
        return render_template("index.html",
                               articles=articles, username=get_user())
    else:
        articles = articles.get_five_more_recent()
        return render_template("index.html",
                               articles=articles, username=get_user())


@app.route("/article/<identifiant>", methods=["GET"])
def show_article(identifiant):
    article = Article().get_article(identifiant)
    if(article is None):
        return render_template("/errors/404.html"), 404
    return render_template("article/view_article.html", article=article,
                           username=get_user())


@app.route("/edit/<identifiant>", methods=["GET", "POST"])
@authentication_required
def edit_article(identifiant):
    article = Article()
    if request.method == "GET":
        article = article.get_article(identifiant)
        if (article is None):
            return render_template("/errors/404.html"), 404
        return render_template("article/edit_article.html", article=article,
                               username=get_user())
    else:
        status = article.update(identifiant, request.form)
        if (status == "success"):
            message = {"status": "success", "message": "Article updated"}
            flash(message)
        else:
            message = {"status": "danger", "message": "An error occured"}
            flash(message)
        article = article.get_article(identifiant)
        return render_template("article/edit_article.html", article=article,
                               username=get_user())


@app.route("/admin", methods=["GET"])
@authentication_required
def admin():
    all_articles = Article().get_all_articles()
    return render_template("article/list_article.html", articles=all_articles,
                           username=get_user())


@app.route("/article/create", methods=["GET", "POST"])
@authentication_required
def new_admin():
    if request.method == "GET":
        return render_template("article/create_article.html",
                               action="/article/create", article="",
                               username=get_user())
    else:
        obj = Article().create_article(request.form)
        if(obj["status"] == "success"):
            message = {"status": "success", "message": "Article created"}
            flash(message)
        else:
            message = {"status": "danger",
                       "message": "All input are required " +
                                  "and id must be unique."}
            flash(message)

        return render_template("article/create_article.html",
                               article=obj["obj"],
                               username=get_user())


@app.route("/invite", methods=["GET", "POST"])
@authentication_required
def invite_guest():
    if request.method == "GET":
        return render_template("admin/invite.html", username=get_user())
    else:
        email = request.form["email"]

        email_regex = re.compile(r"[^@]+@[^@]+\.[^@]+")
        if not email_regex.match(email) or email == "":
            message = {"status": "danger",
                       "message": "Email is required an "
                       "must be in the right format"}
            flash(message)
            return redirect("invite")

        token = uuid.uuid4().hex
        Database().create_user(None, email, None, None, token)
        html = render_template(
            'email/activate.html',
            confirm_url="http://localhost:5000/create/user/" + token)
        send_email(email, "Invitation request", html)
        message = {"status": "success", "message": "Email sended to: "+email}
        flash(message)
        return redirect("/")


@app.route("/create/user/<token>", methods=["GET", "POST"])
def create_user(token):
    if request.method == "GET":
        user = Database().get_user_by_token(token)
        if user:
            return render_template("user/create.html", token=token)
        else:
            message = {"status": "danger",
                       "message": "A valid token is required"}
            flash(message)
            return redirect("/")
    else:
        username = request.form["username"]
        password = request.form["password"]
        if username == "" or password == "":
            message = {"status": "danger",
                       "message": "All fields are required."}
            flash(message)
            return redirect("/create/user/"+token)

        username_exist = Database().check_username(username)
        if username_exist is None:
            salt = uuid.uuid4().hex
            hashed_password = hashlib.sha512(password + salt).hexdigest()
            Database().update_user(token, username, salt, hashed_password)
        else:
            message = {"status": "danger", "message": "Username already used."}
            flash(message)
            return redirect("/create/user/" + token)

        return redirect("/")


@app.route("/forgot", methods=["GET", "POST"])
def forgot_password():
    if request.method == "GET":
        return render_template("recovery_password/forgot.html")
    else:
        email = request.form["email"]
        if email is not None:
            user = Database().get_user_by_email(email)
            if user is not None:
                token = user[6]

                html = render_template(
                    'email/recover.html',
                    confirm_url="http://localhost:5000/recover/" + token)
                send_email(email, "Recover password", html)
                message = {"status": "success",
                           "message": "Recover email sended to: " + email}
                flash(message)
            else:
                message = {"status": "danger", "message": "No user associated"
                                                          " to this email:" +
                                                          email}
                flash(message)
                return redirect("/forgot")


@app.route("/recover/<token>", methods=["GET", "POST"])
def recover_password(token):
    if request.method == "GET":
        if Database().get_user_by_token(token) is not None:
            user = Database().get_user_by_token(token)
            return render_template("recovery_password/recover.html",
                                   email=user[2], token=token)
        else:
            message = {"status": "danger", "message": "Not a valid token"}
            flash(message)
            return redirect("/")
    else:
        if Database().get_user_by_token(token) is not None:
            password = request.form["password"]
            if password is not None:
                user = Database().get_user_by_token(token)
                username = user[1]
                salt = uuid.uuid4().hex
                hashed_password = hashlib.sha512(password + salt).hexdigest()
                Database().update_user(token, username, salt, hashed_password)
                message = {"status": "success", "message":
                           "Password have been reset"}
                flash(message)
                return redirect("/")
            else:
                message = {"status": "danger",
                           "message": "All fields are required."}
                flash(message)
                return redirect("/recover/" + token)
        else:
            message = {"status": "danger", "message": "Not a valid token"}
            flash(message)
            return redirect("/")


# check unicity of article id
@app.route("/checkId", methods=["POST"])
def check_id():
    data = request.get_json()
    id_exist = False

    if Article().get_article(data["identifiant"]) is not None:
        id_exist = True

    return jsonify({"idExist": id_exist})


# api route
@app.route("/api/article/create", methods=["POST"])
def create_article():
    data = request.get_json()
    response = Article().create_article(data)
    status_code = 400
    if response["status"] == "success":
        status_code = 201
    return jsonify(response), status_code


@app.route("/api/article/list", methods=["GET"])
def list_article():
    listarticle = Article().get_all_articles()
    data = [{"title": each[1], "author": each[3],
             "url": "/article/"+urllib.quote(each[2], safe="")} for each in listarticle]
    return jsonify(data)


@app.route("/api/article/<identifiant>", methods=["GET"])
def get_article(identifiant):
    article = Article().get_article(identifiant)
    status_code = 400
    data = {"error": "DisplayId not found"}
    if article is not None:
        status_code = 200
        data = {"_id": article[0], "displayId": article[2],
                "title": article[1], "author": article[3],
                "date": article[4], "paragraph": article[5]}
    return jsonify(data), status_code


@app.errorhandler(404)
def page_not_found(e):
    app.logger.info(e)
    return render_template('/errors/404.html'), 404


@app.errorhandler(500)
def page_not_found(e):
    app.logger.info(e)
    return render_template('/errors/500.html'), 500

if __name__ == "__main__":
    handler = RotatingFileHandler('log_info.log',
                                  maxBytes=10000, backupCount=1)
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)
    app.run(debug=True)
