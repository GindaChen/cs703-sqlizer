import sqlite3, os
from database.engine import LoadDatabase, CloseDatabase
from database.table import getDatabase

def buildTestMASDatabase():
    conn = sqlite3.connect("test_mas.db")
    cur = conn.cursor()
    cur.execute('CREATE TABLE Journal (\n'\
        'jid INTEGER PRIMARY KEY NOT NULL,\n'\
        'name TEXT NOT NULL,\n'\
        'fullName TEXT NOT NULL\n'\
        ')')
    cur.execute('CREATE TABLE Conference (\n'\
        'cid INTEGER PRIMARY KEY NOT NULL,\n'\
        'name TEXT NOT NULL,\n'\
        'fullName TEXT NOT NULL\n'\
        ')')
    cur.execute('CREATE TABLE Author (\n'\
        'aid INTEGER PRIMARY KEY NOT NULL,\n'\
        'name TEXT NOT NULL\n'\
        ')')
    cur.execute('CREATE TABLE Writes (\n'\
        'aid INTEGER NOT NULL,\n'\
        'pid INTEGER NOT NULL,\n'\
        'PRIMARY KEY (aid, pid),\n'
        'FOREIGN KEY (pid) REFERENCES Publication(pid)\n'\
        'FOREIGN KEY (aid) REFERENCES Author(aid)\n'\
        ')')
    cur.execute('CREATE TABLE Publication (\n'\
        'pid INTEGER PRIMARY KEY NOT NULL,\n'\
        'title TEXT NOT NULL,\n'\
        'abstract TEXT NOT NULL,\n'\
        'year INTEGER NOT NULL,\n'\
        'cid INTEGER NOT NULL,\n'\
        'jid INTEGER NOT NULL,\n'\
        'FOREIGN KEY (cid) REFERENCES Conference(cid)\n'\
        'FOREIGN KEY (jid) REFERENCES Journal(jid)\n'
        ')')
    conn.commit()
    conn.close()

def test_LoadDatabase():
    if os.path.exists("test_mas.db"):
        print("skip building MAS database")
    else:
        buildTestMASDatabase()
    LoadDatabase("test_mas.db")
    db = getDatabase()
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
