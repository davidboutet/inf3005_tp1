from database import Database


class Article:
    # def __init__(self, title, identifiant, author, date, paragraph):
    #     self.title = title
    #     self.identifiant = id(self)
    #     self.author = author
    #     self.date = date
    #     self.paragraph = paragraph

    def get_five_more_recent(self):
        db = Database()
        connection = db.get_db()
        cursor = connection.cursor()
        fiveArticle = cursor.execute("select * from article "
                                     "where date_publication < date() "
                                     "order by date_publication "
                                     "limit 5")
        return fiveArticle

    def get_all_articles(self):
        db = Database()
        connection = db.get_db()
        cursor = connection.cursor()
        allArticles = cursor.execute("select * from article")
        return allArticles

    def get_article(self, identifiant):
        db = Database()
        connection = db.get_db()
        cursor = connection.cursor()
        query = "select * from article where identifiant=?"
        row = cursor.execute(query, (identifiant,)).fetchone()
        return row

    def create_article(self, args):
        return_value = {"status": "error", "obj": {}}
        if (args["title"] != "" and args["identifiant"] != "" and
            args["author"] != "" and args["publication_date"] != "" and
            args["paragraph"] != ""):
                db = Database()
                connection = db.get_db()
                cursor = connection.cursor()
                query = "insert into article values (?, ?, ?, ?, ?, ?)"
                data = (id(self), args["title"], args["identifiant"],
                        args["author"], args["publication_date"],
                        args["paragraph"])
                cursor.execute(query, data)
                connection.commit()
                return_value["status"] = "success"
        else:
            return_value["obj"] = (id(self), args["title"],
                                   args["identifiant"],
                                   args["author"], args["publication_date"],
                                   args["paragraph"])
        return return_value

    def update(self, identifiant, args):
        status = "error"
        if (args["title"] != "" and args["paragraph"] != ""):
                db = Database()
                connection = db.get_db()
                cursor = connection.cursor()
                query = "update article " \
                        "set titre = ?, " \
                        "paragraphe = ? " \
                        "where identifiant = ?"
                data = (args["title"], args["paragraph"], identifiant)
                cursor.execute(query, data)
                connection.commit()
                status = "success"
        return status

    def search(self, query_string):
        if(query_string):
            db = Database()
            connection = db.get_db()
            cursor = connection.cursor()
            query = "select * from article " \
                    "where (titre like ? " \
                    "or paragraphe like ?)" \
                    "and date_publication < date()"
            data = ("%"+query_string+"%", "%"+query_string+"%")
            rows = cursor.execute(query, data)
            return rows
