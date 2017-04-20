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

    def create_user(self, username, email, salt, hashed_password, token):
        connection = self.get_db()
        connection.execute(("insert into users(utilisateur, email, salt, "
                            "hash, validated, token)"
                            " values(?, ?, ?, ?, ?, ?)"),
                           (username,
                            email, salt,
                            hashed_password, False, token))
        connection.commit()

    def get_user_by_token(self, token):
        connection = self.get_db()
        cursor = connection.cursor()
        cursor.execute(("select * from users where token=?"),
                       (token,))
        user = cursor.fetchone()
        return user

    def update_user(self, token, username, salt, hashed_password):
        connection = self.get_db()
        connection.execute(("update users set utilisateur=?, salt=?, "
                            "hash=?, validated=? where token=?"),
                           (username, salt, hashed_password, True, token))
        connection.commit()

    def check_username(self, username):
        cursor = self.get_db().cursor()
        cursor.execute(("select * from users where utilisateur=?"),
                       (username,))
        return cursor.fetchone()

    def get_user_login_info(self, username):
        cursor = self.get_db().cursor()
        cursor.execute(("select salt, hash from users where utilisateur=?"),
                       (username,))
        user = cursor.fetchone()
        if user is None:
            return None
        else:
            return user[0], user[1]

    def save_session(self, id_session, username):
        connection = self.get_db()
        connection.execute(("insert into sessions(id_session, utilisateur) "
                            "values(?, ?)"), (id_session, username))
        connection.commit()

    def delete_session(self, id_session):
        connection = self.get_db()
        connection.execute(("delete from sessions where id_session=?"),
                           (id_session,))
        connection.commit()

    def get_session(self, id_session):
        cursor = self.get_db().cursor()
        cursor.execute(("select utilisateur from sessions where id_session=?"),
                       (id_session,))
        data = cursor.fetchone()
        if data is None:
            return None
        else:
            return data[0]
