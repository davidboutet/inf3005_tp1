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
        fiveArticle = connection.execute("select * from article where date_publication < date() order by date_publication limit 5").fetchall()
        return fiveArticle


    def get_article(self, id):
        db = Database()
        connection = db.get_db()
        print connection.execute("select * from article").fetchall()

    def create_article(self, args):
        status = "Error"
        if (args["title"] != "" and args["identifiant"] != "" and args["author"] != ""
            and args["publication_date"] != "" and args["paragraph"] != ""):
            db = Database()
            connection = db.get_db()
            connection.execute("insert into article values (?, ?, ?, ?, ?, ?)", (id(self),
                                                                                 args["title"],
                                                                                 args["identifiant"],
                                                                                 args["author"],
                                                                                 args["publication_date"],
                                                                                 args["paragraph"]))
            connection.commit()
            status = "Success"
            return status




