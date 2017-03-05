from flask import g
import sqlite3

class Database:
    def __init__(self):
        self.connection = None
        self.path = "database/db.db"


    def get_db(self):
        db = getattr(g, '_database', None)
        if db is None:
            db = g._database = sqlite3.connect(self.path)
        return db