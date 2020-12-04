from database.table import pushDatabase, getDatabase
from query.type import numeric, string, boolean


def getSimpleDB():
    pushDatabase("db_test_simple")
    db = getDatabase()

    db.add_table("t1")
    db.add_table("t2")

    t1 = db["t1"]
    t2 = db["t2"]
    t1.add_column("c11", numeric)
    t1.add_column("c12", string)
    t1.add_column("c13", boolean)
    t2.add_column("c21", numeric)
    t2.add_column("c22", string)
    return db


def getForeignDB():
    pushDatabase("db_test_foreign")
    db = getDatabase()

    db.add_table("author")
    db.add_table("papers")

    t1 = db["author"]
    t2 = db["papers"]
    t1.add_column("id", numeric)
    t1.add_column("name", string)
    t1.add_column("is_student", boolean)
    t2.add_column("pages", numeric)
    t2.add_column("title", string)
    t2.add_column("author_name", string, foreign_of=t1["name"])

    return db


def getTinyDB():
    pushDatabase("db_test_tiny")
    db = getDatabase()

    db.add_table("author")

    t1 = db["author"]
    t1.add_column("id", numeric)
    t1.add_column("name", string)
    t1.add_column("is_student", boolean)

    return db
