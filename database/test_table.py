from database.table import Database
from query.type import numeric, boolean


def test_database_basic():
    db = Database(name='default')
    t = db.add_table(name='titanic')
    c = t.add_column(name='Age')

    assert str(t) == 'titanic'
    assert str(c) == 'titanic.Age'

    assert db.tables == {'titanic': t}
    assert t.columns == {'Age': c}


def test_database_with_schema():
    db = Database(name='default')
    t = db.add_table(name='titanic')
    c1 = t.add_column(name='Age', type_=numeric)
    c2 = t.add_column(name='Survived', type_=boolean)

    assert c1.schema() == 'numeric'
    assert c2.schema() == 'boolean'
    assert t.schema() == '{(Age: numeric), (Survived: boolean)}'
