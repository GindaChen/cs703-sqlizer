"""
When initializing a database, the following objects are pre-initialized.
So when the
"""
import sqlite3
from sqlite3 import Connection
from typing import Dict
from query.type import Type, boolean, numeric, string
# from query.infer import BaseSketchCompl
# from query.expr import Aggregation


class DatabaseColumn():
    def __init__(self, name: str, table: 'DatabaseTable', type_: Type=None, foreign_of:'DatabaseColumn'=None, is_primary=False):
        self.cname = name or ""
        self.table: 'DatabaseTable' = table
        self.info = {}
        self.type_ = type_
        self.foreign_of = foreign_of
        self.is_primary = is_primary

    @property
    def name(self) -> str:
        """Suppose the qualified name is <tname>.<cname>"""
        tname = self.table.name
        cname = self.cname
        return f'{tname}.{cname}'

    def __repr__(self):
        return self.name

    def schema(self):
        return f'{self.type_}'

    # below are just some "fake" DatabaseColumn, which is used for type checking

    # construct a temperate DatabaseColumn from an aggreation function
    # this is used for type inference
    @classmethod
    def aggDatabaseColumn(cls, agg_expr):
        # agg_expr is an instance of Aggregation
        # TODO: current implementation might work, but may need more tests
        return DatabaseColumn(name=f'agg_tmp', table=None, type_=agg_expr.func.output_type)

    @classmethod
    def valueDatabaseColumn(cls, type_):
        # TODO: current implementation might work, but may need more tests
        return DatabaseColumn(name=f'val_tmp', table=None, type_=type_)


class DatabaseTable():
    def __init__(self, name: str, database: 'Database' = None):
        self.tname = name
        self.database: 'Database' = database
        self.info = {}
        self.columns: Dict[str, DatabaseColumn] = {}

    @property
    def name(self) -> str:
        return self.tname

    def __repr__(self):
        return self.name

    # foreign_of is not None if the column to be added is a foreign key refers to another column
    def add_column(self, name, type_=None, foreign_of:DatabaseColumn=None):
        if name in self.columns:
            raise KeyError(f'Table {self.name} already have column {name}.')
        column = DatabaseColumn(name=name, table=self, type_=type_, foreign_of=foreign_of)
        self.columns[name] = column
        return column

    def schema(self):
        sub_schema = [f'({i}: {v.schema()})' for i, v in self.columns.items()]
        return '{' + ', '.join(sub_schema) + '}'

    def __getitem__(self, item):
        return self.columns[item]

    def getAllColumnNames(self):
        return self.columns.keys()

    def getAllColumns(self):
        return self.columns.items()

    def getAllColumnObjs(self):
        return self.columns.values()


class Database():
    def __init__(self, name, conn=None):
        self.name = name
        self.info = {}
        self.tables = {}
        self.conn: Connection = conn

    def add_table(self, name):
        if name in self.tables:
            raise KeyError(f'Database {self.name} already have table {name}.')
        table = DatabaseTable(name=name, database=self)
        self.tables[name] = table
        return table

    def __getitem__(self, item) -> DatabaseTable:
        return self.tables[item]

    def getAllTableNames(self):
        return self.tables.keys()

    def getAllTables(self):
        return self.tables.items()

    def evalPred(self, pred_expr: 'Predicate', c_sketch_compl: 'BaseSketchCompl', e_sketch_compl: 'BaseSketchCompl'):
        db = getDatabase()
        if db.conn is None:
            return True
        lhs = pred_expr.args[0].unparse(sketch_compl = c_sketch_compl)
        rhs = pred_expr.args[1].unparse(sketch_compl = e_sketch_compl)
        pred_str = f'({lhs} {pred_expr.func.name} {rhs})'
        possible_tables = set()
        for db_col in c_sketch_compl.type_check.type_set:
            possible_tables.add(db_col.table)
        for table in possible_tables:
            table_name = table.tname
            sql_str = f"SELECT {lhs}\nFROM {table_name}\nWHERE {pred_str}"
            cur = self.conn.cursor()
            try:
                if cur.execute(sql_str).fetchone() is not None:
                    return True
            except sqlite3.Error:
                return False
            finally:
                cur.close()
        return False

    def setPrimaryForeign(self, primary_table_name: str, primary_column_name: str, foreign_table_name: str, foreign_column_name: str):
        primary_col = self[primary_table_name][primary_column_name]
        foreign_col = self[foreign_table_name][foreign_column_name]
        primary_col.is_primary = True
        foreign_col.foreign_of = primary_col


# DatabaseMgr makes multiple database coexist possible
# this is useful to testing where db is built by the test case itself
# Do not export DatabaseMgr or DBMgr
# use pushDatabase(), getDatabase(), and popDatabase() to access Database instance
class DatabaseMgr():
    def __init__(self):
        from collections import deque
        self.db_stack = deque()

    def pushDatabase(self, name, conn):
        self.db_stack.append(Database(name, conn))

    def popDatabase(self):
        self.db_stack.pop()

    def getDatabase(self):
        return self.db_stack[-1]


DBMgr = DatabaseMgr()


def pushDatabase(name, conn=None):
    DBMgr.pushDatabase(name, conn=conn)


def popDatabase():
    DBMgr.popDatabase()


def getDatabase() -> Database:
    return DBMgr.getDatabase()
