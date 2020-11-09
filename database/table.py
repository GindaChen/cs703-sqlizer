"""
When initializing a database, the following objects are pre-initialized.
So when the
"""


class DatabaseColumn():
    def __init__(self, name: str = None, table: 'DatabaseTable' = None):
        self.cname = name or ""
        self.table: 'DatabaseTable' = table
        self.info = {}

    @property
    def name(self) -> str:
        """Suppose the qualified name is <tname>.<cname>"""
        tname = self.table.tname
        cname = self.cname
        return f'{tname}.{cname}'


class DatabaseTable():
    def __init__(self, name: str, database: 'Database' = None):
        self.tname = name
        self.database: 'Database' = database
        self.info = {}

    @property
    def name(self) -> str:
        return self.name

class Database():
    def __init__(self, name):
        self.name = name
        self.info = {}
    pass
