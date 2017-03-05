from flask import Flask, request, render_template, redirect, g, flash
from database import Database
from article import Article
import sqlite3
import logging
from logging.handlers import RotatingFileHandler

app = Flask(__name__, static_url_path="", static_folder="static")
app.secret_key = 'secretKey'


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route("/", methods=["GET"])
def index():
    # logging
    # app.logger.info('Info')
    articles = Article()
    return render_template("index.html", articles=articles.get_five_more_recent())


@app.route("/article/<identifiant>", methods=["GET"])
def show_article(identifiant):
    return True


@app.route("/admin", methods=["GET"])
def admin():
    return True


@app.route("/admin-nouveau", methods=["GET", "POST"])
def new_admin():
    if request.method == "GET":
        return render_template("article/article_form.html", action="/admin-nouveau")
    else:
        article = Article()
        article.create_article(request.form)
        return render_template("article/article_form.html")


if __name__ == "__main__":
    handler = RotatingFileHandler('log_info.log', maxBytes=10000, backupCount=1)
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)
    app.run(debug=True)
