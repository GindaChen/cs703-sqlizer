"""
When initializing a database, the following objects are pre-initialized.
So when the
"""
from typing import Dict
from query.type import Type, boolean, numeric, string
from query.infer import BaseSketchCompl
from query.expr import Aggregation, Value

class DatabaseColumn():
    def __init__(self, name: str, table: 'DatabaseTable', type_: Type=None):
        self.cname = name or ""
        self.table: 'DatabaseTable' = table
        self.info = {}
        self.type_ = type_

    @property
    def name(self) -> str:
        """Suppose the qualified name is <tname>.<cname>"""
        tname = self.table.name
        cname = self.cname
        return f'{tname}.{cname}'

    def __str__(self):
        return self.name

    def schema(self):
        return f'{self.type_}'

    # below are just some "fake" DatabaseColumn, which is used for type checking

    # construct a temperate DatabaseColumn from an aggreation function
    # this is used for type inference
    @classmethod
    def aggDatabaseColumn(cls, agg_expr: Aggregation, sketch_compl: BaseSketchCompl):
        # TODO: current implementation might work, but may need more tests
        return DatabaseColumn(name=f'agg_tmp', table=None, type_=agg_expr.func.output_type)
    
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

    def __str__(self):
        return self.name

    def add_column(self, name, type_=None):
        if name in self.columns:
            raise KeyError(f'Table {self.name} already have column {name}.')
        column = DatabaseColumn(name=name, table=self, type_=type_)
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
    def __init__(self, name):
        self.name = name
        self.info = {}
        self.tables = {}

    def add_table(self, name):
        if name in self.tables:
            raise KeyError(f'Database {self.name} already have table {name}.')
        table = DatabaseTable(name=name, database=self)
        self.tables[name] = table
        return table

    def __getitem__(self, item):
        return self.tables[item]

    def getAllTableNames(self):
        return self.tables.keys()

    def getAllTables(self):
        return self.tables.items()


db = Database("PlaceHolder") # going to be replaced with real one...
