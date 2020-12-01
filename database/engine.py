import sqlite3
import os
from database.table import pushDatabase, popDatabase, getDatabase
from query.type import boolean, numeric, string

def LoadDatabase(path, db_name=None):
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    schema = cur.execute('SELECT tbl_name, sql FROM sqlite_master WHERE type = "table"')
    if db_name is None:
        db_name = os.path.basename(path)
    pushDatabase(db_name, conn)
    db = getDatabase()
    foreign_refs = [] # (primary table name, primary column name, foreign table name, foreign column name)
    for tbl_name, sql in schema.fetchall():
        db.add_table(tbl_name)
        tbl = db[tbl_name]
        # the first line is "CREATE ...("
        # the last line is a single ")"
        # skip them
        for line_num in range(1, len(sql) - 1):
            line_str = sql[line_num].split()
            if line_str[1] == "KEY":
                if line_str[0] == "PRIMARY":
                    pass # set is_primary will be done by Database.setPrimaryForeign()
                elif line_str[0] == "FOREIGN":
                    ref_idx = 0
                    for ref_idx in range(2, len(line_str)):
                        if line_str[ref_idx] == "REFERENCES":
                            break
                    tmp = line_str[ref_idx + 1].split("(")
                    primary_table_name = tmp[0]
                    line_str[ref_idx + 1] = tmp[1].strip("(),")
                    for i in range(2, ref_idx):
                        foreign_refs.append((primary_table_name, line_str[i + ref_idx - 1].strip("(),"), \
                            tbl_name, line_str[i].strip("(),"), ))
                else:
                    raise ValueError("Sqlite schema parse failed")
            else:
                if line_str[1] == "INTEGER":
                    type_ = numeric
                elif line_str[1] == "TEXT":
                    type_ = string
                else:
                    raise TypeError(f"Unsupported Type: {line_str[1]}")
                tbl.add_column(line_str[0], type_)
    
    for pt, pc, ft, fc in foreign_refs:
        db.setPrimaryForeign(pt, pc, ft, fc)


def CloseDatabase():
    db = getDatabase()
    if db.conn is not None:
        db.conn.close()
    popDatabase()
