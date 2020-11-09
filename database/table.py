"""
When initializing a database, the following objects are pre-initialized.
So when the
"""


class DatabaseColumn():
    def __init__(self, name: str = None, table: 'DatabaseTable' = None):
        self.name = name or ""
        self.table: 'DatabaseTable' = table
        self.info = {}
    pass


class DatabaseTable():
    def __init__(self, name: str, database: 'Database' = None):
        self.name = name
        self.database: 'Database' = database
        self.info = {}
    pass

class Database():
    def __init__(self, name):
        self.name = name
        self.info = {}
    pass
