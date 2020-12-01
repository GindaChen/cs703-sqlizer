import sqlite3
import os
from database.table import pushDatabase, popDatabase, getDatabase
from query.type import boolean, numeric, string

def LoadDatabase(path, db_name=None):
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    schema = cur.execute('SELECT tbl_name FROM sqlite_master WHERE type = "table"')
    if db_name is None:
        db_name = os.path.basename(path)
    pushDatabase(db_name, conn)
    db = getDatabase()
    foreign_refs = [] # (primary table name, primary column name, foreign table name, foreign column name)
    for tbl_name, in schema.fetchall():
        db.add_table(tbl_name)
        tbl = db[tbl_name]
        for row in cur.execute(f'PRAGMA table_info("{tbl_name}")'):
            col_name = row[1]
            if row[2] == "INTEGER":
                col_type = numeric
            elif row[2] == "TEXT":
                col_type = string
            else:
                raise TypeError(f"Unsupported Type: {row[2]}")
            tbl.add_column(col_name, col_type)
        for row in cur.execute(f'PRAGMA foreign_key_list("{tbl_name}")'):
            foreign_refs.append((row[2], row[4], tbl_name, row[3]))
    for pt, pc, ft, fc in foreign_refs:
        db.setPrimaryForeign(pt, pc, ft, fc)


def CloseDatabase():
    db = getDatabase()
    if db.conn is not None:
        db.conn.close()
    popDatabase()
