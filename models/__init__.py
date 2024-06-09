from flask_mysqldb import MySQL


mysql = MySQL()


db = None


def get_db():
    global db

    if db:
        return db
    else:
        db = mysql
        return db
