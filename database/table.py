"""
When initializing a database, the following objects are pre-initialized.
So when the
"""
from typing import Dict


class DatabaseColumn():
    def __init__(self, name: str, table: 'DatabaseTable', type_=None):
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
