from database.table import DatabaseColumn, DatabaseTable, Database


def test_database_table_basic():
    db = Database(name='default')
    t = db.add_table(name='titanic')
    c = t.add_column(name='Age')

    assert str(t) == 'titanic'
    assert str(c) == 'titanic.Age'

    assert db.tables == {'titanic': t}
    assert t.columns == {'Age': c}