db = None


def get_db():
    global db

    if db:
        return db
    else:
        from app import mysql
        db = mysql
        return db
