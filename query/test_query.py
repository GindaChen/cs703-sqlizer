from pytest import fixture

from database.default_db import construct_default_db
from database.table import DatabaseTable
from query.expr import Column, Table
from query.operators import all_aggregates


@fixture
def titanic() -> DatabaseTable:
    db = construct_default_db()
    yield db['titanic']


def test_column_basic(titanic):
    c = Column('Age')
    assert str(c) == 'Age'

    c = Column()
    assert str(c) == '?'

    c = Column(hint=['papers'])
    assert str(c) == '?[papers]'

    c = Column(hint=['papers', '10'])
    assert str(c) == '?[papers, 10]'

    c = Column(titanic['Age'])
    assert str(c) == 'titanic.Age'


def test_table_basic(titanic):
    t = Table('Tb')
    assert str(t) == 'Tb'

    t = Table()
    assert str(t) == '??'

    t = Table(hint=['unique'])
    assert str(t) == '??[unique]'

    t = Table(titanic)
    assert str(t) == 'titanic'


def test_aggregate_basic():
    c = Column('Age')
    for f in all_aggregates:
        e = f(c)
        assert str(e) == f'{e.func}({c.value})'

    c = Column(hint=['papers', '10'])
    for f in all_aggregates:
        e = f(c)
        assert str(e) == f'{e.func}({str(c)})'


def test_predicate_basic():
    c = Column('Age')
    p1 = (c == 1)
    p2 = (c == 2)

    p = p1.and_(p2)
    assert str(p) == '((Age = 1) AND (Age = 2))'

    p = p1.or_(p2)
    assert str(p) == '((Age = 1) OR (Age = 2))'

    p = p1.not_()
    assert str(p) == '!((Age = 1))'

    p3 = (c < 1)
    assert str(p3) == '(Age < 1)'

    p3 = (c > 4)
    assert str(p3) == '(Age > 4)'


def test_projection_basic(titanic: DatabaseTable):
    t = Table()
    pass





