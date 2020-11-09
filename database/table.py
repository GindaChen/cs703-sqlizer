"""
When initializing a database, the following objects are pre-initialized.
So when the
"""


class DatabaseColumn():
    def __init__(self, name: str, table: 'DatabaseTable'):
        self.cname = name or ""
        self.table: 'DatabaseTable' = table
        self.info = {}

    @property
    def name(self) -> str:
        """Suppose the qualified name is <tname>.<cname>"""
        tname = self.table.name
        cname = self.cname
        return f'{tname}.{cname}'

    def __str__(self):
        return self.name


class DatabaseTable():
    def __init__(self, name: str, database: 'Database' = None):
        self.tname = name
        self.database: 'Database' = database
        self.info = {}
        self.columns = {}

    @property
    def name(self) -> str:
        return self.tname

    def __str__(self):
        return self.name

    def add_column(self, name):
        if name in self.columns:
            raise KeyError(f'Table {self.name} already have column {name}.')
        column = DatabaseColumn(name=name, table=self)
        self.columns[name] = column
        return column


class Database():
    def __init__(self, name):
        self.name = name
        self.info = {}
        self.tables = {}

    pass

    def add_table(self, name):
        if name in self.tables:
            raise KeyError(f'Database {self.name} already have table {name}.')
        table = DatabaseTable(name=name, database=self)
        self.tables[name] = table
        return table
