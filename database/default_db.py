from database.table import Database
from query.type import numeric, boolean, string

def construct_default_db() -> Database:
    """Construct default database with a column titanic."""
    default_db = Database('default')
    titanic = default_db.add_table('titanic')
    titanic_columns = {
        'Age': {'type_': numeric},
        'Survived': {'type_': boolean},
        'Fare': {'type_': numeric},
        'Name': {'type_': string},
    }
    for cname, info in titanic_columns.items():
        titanic.add_column(name=cname, **info)

    return default_db

default_db = construct_default_db()