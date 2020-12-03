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
    cur.executescript("""
        CREATE TABLE Journal (
            jid INTEGER PRIMARY KEY,
            name TEXT,
            fullName TEXT
        );
        
        CREATE TABLE Conference (
            cid INTEGER PRIMARY KEY,
            name TEXT,
            fullName TEXT
        );
        
        CREATE TABLE Author (
            aid INTEGER PRIMARY KEY,
            name TEXT
        );
        
        CREATE TABLE Writes (
            aid INTEGER,
            pid INTEGER,
            PRIMARY KEY (aid, pid),
            FOREIGN KEY (pid) REFERENCES Publication(pid),
            FOREIGN KEY (aid) REFERENCES Author(aid)
        );
        
        CREATE TABLE Publication (
            pid INTEGER PRIMARY KEY,
            title TEXT,
            abstract TEXT,
            year INTEGER,
            cid INTEGER,
            jid INTEGER,
            FOREIGN KEY (cid) REFERENCES Conference(cid),
            FOREIGN KEY (jid) REFERENCES Journal(jid)
        );
        
        INSERT INTO Author VALUES (1, "Navid Yaghmazadeh");
        INSERT INTO Author VALUES (2, "Yuepeng Wang");
        INSERT INTO Author VALUES (3, "Isil Dillig");
        INSERT INTO Author VALUES (4, "Thomas Dillig");
        INSERT INTO Conference VALUES (11, "OOPSLA", "Object-Oriented Programming, Systems, Languages & Applications");
        INSERT INTO Publication VALUES (21, "SQLizer: Query Synthesis from Natural Language", "SQLizer's abstract", 2017, 11, NULL);
        INSERT INTO Writes VALUES (1, 21);
        INSERT INTO Writes VALUES (2, 21);
        INSERT INTO Writes VALUES (3, 21);
        INSERT INTO Writes VALUES (4, 21);
    """)
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
    v1 = Value(2017)
    v2 = Value(2021)
    pred_true = Predicate(ops.eq, c, v1)
    pred_false = Predicate(ops.eq, c, v2)
    type_check = TypeCheck(set(db["Publication"].getAllColumnObjs()))
    assert db.evalPred(pred_true, c.getCandidates(type_check)[0], v1.getCandidates(type_check)[0])
    assert not db.evalPred(pred_false, c.getCandidates(type_check)[0], v2.getCandidates(type_check)[0])
    CloseDatabase()
