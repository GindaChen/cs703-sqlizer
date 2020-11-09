from database.table import DatabaseColumn, DatabaseTable, Database


def test_database_table_basic():
    db = Database(name='default')
    t = DatabaseTable(name='titanic')
    c = DatabaseColumn(name='Age', table=t)
    assert str(t) == 'titanic'
    assert str(c) == 'titanic.Age'

