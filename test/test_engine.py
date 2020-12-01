import sqlite3, os
from database.engine import LoadDatabase, CloseDatabase
from database.table import getDatabase
from query.expr import Predicate, Column, Value
from query.base import Hint
from query.infer import TypeCheck
import query.operators as ops


def buildTestMASDatabase():
    conn = sqlite3.connect("test_mas.db")
    cur = conn.cursor()
    # create table
    cur.execute('CREATE TABLE Journal (\n'\
        'jid INTEGER PRIMARY KEY,\n'\
        'name TEXT,\n'\
        'fullName TEXT\n'\
        ')')
    cur.execute('CREATE TABLE Conference (\n'\
        'cid INTEGER PRIMARY KEY,\n'\
        'name TEXT,\n'\
        'fullName TEXT\n'\
        ')')
    cur.execute('CREATE TABLE Author (\n'\
        'aid INTEGER PRIMARY KEY,\n'\
        'name TEXT\n'\
        ')')
    cur.execute('CREATE TABLE Writes (\n'\
        'aid INTEGER,\n'\
        'pid INTEGER,\n'\
        'PRIMARY KEY (aid, pid),\n'
        'FOREIGN KEY (pid) REFERENCES Publication(pid)\n'\
        'FOREIGN KEY (aid) REFERENCES Author(aid)\n'\
        ')')
    cur.execute('CREATE TABLE Publication (\n'\
        'pid INTEGER PRIMARY KEY,\n'\
        'title TEXT,\n'\
        'abstract TEXT,\n'\
        'year INTEGER,\n'\
        'cid INTEGER,\n'\
        'jid INTEGER,\n'\
        'FOREIGN KEY (cid) REFERENCES Conference(cid)\n'\
        'FOREIGN KEY (jid) REFERENCES Journal(jid)\n'
        ')')
    # insert
    cur.execute('INSERT INTO Author VALUES (1, "Navid Yaghmazadeh")')
    cur.execute('INSERT INTO Author VALUES (2, "Yuepeng Wang")')
    cur.execute('INSERT INTO Author VALUES (3, "Isil Dillig")')
    cur.execute('INSERT INTO Author VALUES (4, "Thomas Dillig")')
    cur.execute('INSERT INTO Conference VALUES (11, "OOPSLA", "Object-Oriented Programming, Systems, Languages & Applications")')
    cur.execute('INSERT INTO Publication VALUES (21, "SQLizer: Query Synthesis from Natural Language", '\
        '"SQLizer\'s abstract", 2017, 11, NULL)')
    cur.execute('INSERT INTO Writes VALUES (1, 21)')
    cur.execute('INSERT INTO Writes VALUES (2, 21)')
    cur.execute('INSERT INTO Writes VALUES (3, 21)')
    cur.execute('INSERT INTO Writes VALUES (4, 21)')
    conn.commit()
    conn.close()


def buildTestMASDatabaseIfNotExist():
    if os.path.exists("test_mas.db"):
        print("skip building MAS database")
    else:
        buildTestMASDatabase()


def test_LoadDatabase():
    buildTestMASDatabaseIfNotExist()
    LoadDatabase("test_mas.db")
    db = getDatabase()
    assert db.conn is not None
    assert len(db.getAllTableNames()) == 5
    assert 'Conference' in db.getAllTableNames()
    assert 'Writes' in db.getAllTableNames()
    assert "jid" in db["Journal"].getAllColumnNames()
    assert "name" in db["Author"].getAllColumnNames()
    assert db["Publication"]["cid"].foreign_of is db["Conference"]["cid"]
    assert db["Publication"]["cid"].foreign_of is not db["Journal"]["jid"]
    assert db["Author"]["aid"].is_primary
    assert not db["Journal"]["fullName"].is_primary
    CloseDatabase()


def test_evalPred():
    buildTestMASDatabaseIfNotExist()
    LoadDatabase("test_mas.db")
    db = getDatabase()
    assert db.conn is not None
    c = Column(hint=Hint("year"))
    v1 = Value(2010)
    v2 = Value(2021)
    pred_true = Predicate(ops.eq, c, v1)
    pred_false = Predicate(ops.eq, c, v2)
    type_check = TypeCheck(set(db["Publication"].getAllColumnObjs()))
    assert db.evalPred(pred_true, c.getCandidates(type_check)[0], v1.getCandidates(type_check)[0])
    assert not db.evalPred(pred_false, c.getCandidates(type_check)[0], v2.getCandidates(type_check)[0])
    CloseDatabase()
