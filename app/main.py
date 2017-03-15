from flask import Flask, request, render_template, redirect, g, flash
import logging
from logging.handlers import RotatingFileHandler
from article import Article

app = Flask(__name__, static_url_path="", static_folder="static")
app.secret_key = 'secretKey'


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route("/", methods=["GET", "POST"])
def index():
    articles = Article()
    if request.method == "POST" and request.form["search_string"]:
        query_string = request.form["search_string"]
        articles = articles.search(query_string)
        return render_template("index.html",
                               articles=articles)
    else:
        articles = articles.get_five_more_recent()
        return render_template("index.html",
                               articles=articles)


@app.route("/article/<identifiant>", methods=["GET"])
def show_article(identifiant):
    article = Article()
    article = article.get_article(identifiant)
    if(article is None):
        return render_template("404.html"), 404
    return render_template("article/single_article.html", article=article)


@app.route("/edit/<identifiant>", methods=["GET", "POST"])
def edit_article(identifiant):
    article = Article()
    if request.method == "GET":
        article = article.get_article(identifiant)
        if (article is None):
            return render_template("404.html"), 404
        return render_template("article/edit_article.html", article=article)
    else:
        status = article.update(identifiant, request.form)
        if (status == "success"):
            message = {"status": "success", "message": "Article updated"}
            flash(message)
        else:
            message = {"status": "danger", "message": "An error occured"}
            flash(message)
        article = article.get_article(identifiant)
        return render_template("article/edit_article.html", article=article)


@app.route("/admin", methods=["GET"])
def admin():
    article = Article()
    all_articles = article.get_all_articles()
    return render_template("article/all_articles.html", articles=all_articles)


@app.route("/admin-nouveau", methods=["GET", "POST"])
def new_admin():
    if request.method == "GET":
        return render_template("article/article_form.html",
                               action="/admin-nouveau", article="")
    else:
        article = Article()
        obj = article.create_article(request.form)
        if(obj["status"] == "success"):
            message = {"status": "success", "message": "Article created"}
            flash(message)
        else:
            message = {"status": "danger",
                       "message": "All input are required."}
            flash(message)

        return render_template("article/article_form.html", article=obj["obj"])


@app.errorhandler(404)
def page_not_found(e):
    app.logger.info(e)
    return render_template('404.html'), 404


@app.errorhandler(500)
def page_not_found(e):
    app.logger.info(e)
    return render_template('500.html'), 500

if __name__ == "__main__":
    handler = RotatingFileHandler('log_info.log',
                                  maxBytes=10000, backupCount=1)
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)
    app.run(debug=True)
