from flask import Flask, request, render_template, redirect, g
import logging
from logging.handlers import RotatingFileHandler

DATABASE = "/database/db.db"
app = Flask(__name__, static_url_path="", static_folder="static")


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route("/", methods=["GET"])
def index():
    # connection = database.get_db()
    # cursor = connection.cursor()
    # print cursor.execute("select * from album").fetchall()
    # logging
    # app.logger.info('Info')
    return render_template("index.html")

if __name__ == "__main__":
    handler = RotatingFileHandler('log_info.log', maxBytes=10000, backupCount=1)
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)
    app.run(debug=True)
