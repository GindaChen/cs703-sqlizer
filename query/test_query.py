from pytest import fixture

from database.default_db import construct_default_db
from database.table import DatabaseTable
from query.base import Hint
from query.type import boolean, numeric, string
from query.expr import Entity, AbstractTable, AbstractColumns, Value, Column, \
    Table, GroupAgg, Aggregation, Predicate, Projection, Selection, Join
import query.operators as ops


def test_Column():
    c = Column('Age')
    assert c.unparse() == 'Age'
    assert not c.isHole
    assert c.hint is None

    c = Column(hint=Hint('papers'))
    assert c.unparse() == '?[papers]'
    assert c.isHole


def test_Table():
    t = Table('Publication')
    assert t.unparse() == 'Publication'
    assert not t.isHole
    assert t.hint is None

    t = Table(hint=Hint(['papers', 'publication']))
    assert t.unparse() == '??[papers, publication]'
    assert t.isHole


def test_Value():
    v = Value(233)
    assert v.type == numeric
    assert v.unparse() == "233"

    v = Value("helloworld")
    assert v.type == string
    assert v.unparse() == '"helloworld"'

    v = Value(True)
    assert v.type == boolean
    assert v.unparse() == "True"

# this test includes all its subclass actually
def test_AbstractTable():
    p = Projection(Table("Publication"), AbstractColumns(from_list=[Column("author"), Column("year")]))
    assert p.unparse() == "SELECT author, year\nFROM Publication"

    pp = Projection(p, AbstractColumns(Column("author")))
    assert pp.unparse() == "SELECT author\nFROM (SELECT author, year\n\tFROM Publication)"

    s = Selection(Table("Publication"), Predicate(ops.eq, Column("year"), Value(2010)))
    assert s.unparse() == "Publication\nWHERE (year = 2010)"

    ps = Projection(s, AbstractColumns(Column("author")))
    assert ps.unparse() == "SELECT author\nFROM Publication\nWHERE (year = 2010)"

    j = Join(Table("Publication"), Table("Conference"), AbstractColumns(Column("Publication.cid")), AbstractColumns(Column("Conference.cid")))
    assert j.unparse() == "Publication JOIN Conference ON Publication.cid = Conference.cid"

    psj = Projection(
        Selection(j, Predicate(ops.eq, Column("year"), Value(2010))),
        AbstractColumns(from_list=[Column("author"), Column("year")])
    )
    assert psj.unparse() == "SELECT author, year\nFROM Publication JOIN Conference ON Publication.cid = Conference.cid\nWHERE (year = 2010)"

    psj_withholes = Projection(
        Selection(j, Predicate(ops.eq, Column("year"), Value(2010))),
        AbstractColumns(from_list=[Column(hint=Hint("Loris")), Column("year")])
    )
    assert psj_withholes.unparse() == "SELECT ?[Loris], year\nFROM Publication JOIN Conference ON Publication.cid = Conference.cid\nWHERE (year = 2010)"


def test_Predicate():
    p1 = Predicate(ops.eq, Column(hint=Hint()), Value("OOPSLA"))
    assert p1.unparse() == '(? = "OOPSLA")'
    p2 = Predicate(ops.eq, Column("year"), Value(2010))
    assert p2.unparse() == "(year = 2010)"
    p3 = Predicate(ops.and_, p1, p2)
    assert p3.unparse() == '((? = "OOPSLA") AND (year = 2010))'


def test_Aggregation():
    a1 = Aggregation(ops.count_, Column(hint=Hint("papers")))
    assert a1.unparse() == "count(?[papers])"
    a2 = Aggregation(ops.max_, Column("year"))
    assert a2.unparse() == 'max(year)'
    sql1 = Projection(
        Selection(
            Table(hint=Hint("papers")),
            Predicate(ops.and_,
                      Predicate(ops.eq, Column(hint=Hint()), Value("OOPSLA")),
                      Predicate(ops.eq, Column(hint=Hint()), Value(2010))
            )
        ),
        AbstractColumns(from_list=[a1, a2])
    )
    assert sql1.unparse() == 'SELECT count(?[papers]), max(year)\nFROM ??[papers]\nWHERE ((? = "OOPSLA") AND (? = 2010))'


def test_GroupAgg():
    a1 = Aggregation(ops.count_, Column(hint=Hint("papers")))
    ga1 = GroupAgg(a1, Column("author"))
    sql1 = Projection(
        Selection(
            Table(hint=Hint("papers")),
            Predicate(ops.and_,
                      Predicate(ops.eq, Column(hint=Hint()), Value("OOPSLA")),
                      Predicate(ops.eq, Column(hint=Hint()), Value(2010))
            )
        ),
        AbstractColumns(ga1)
    )
    assert sql1.unparse() == 'SELECT count(?[papers])\nFROM ??[papers]\nWHERE ((? = "OOPSLA") AND (? = 2010))\nGROUP BY author'


def test_AbstractColumns():
    c = Column("name")
    f = Aggregation(ops.count_, Column(hint=Hint("papers")))
    g = GroupAgg(f, Column("author")) # note:
    abs_c0 = AbstractColumns(from_list=[c, f, g])
    abs_c1 = AbstractColumns(c)
    abs_c2 = AbstractColumns(f)
    abs_c3 = AbstractColumns(g)
    abs_c4 = AbstractColumns(lhs=AbstractColumns(lhs=abs_c1, rhs=abs_c2), rhs=abs_c3)
    assert abs_c0.unparse() == 'name, count(?[papers]), count(?[papers])'
    assert abs_c4.unparse() == 'name, count(?[papers]), count(?[papers])'

    sql1 = Projection(Table(hint=Hint("papers")), abs_c4)
    assert sql1.unparse() == 'SELECT name, count(?[papers]), count(?[papers])\nFROM ??[papers]\nGROUP BY author'


# below are unused so far...
@fixture
def titanic() -> DatabaseTable:
    db = construct_default_db()
    yield db['titanic']


def test_column_basic(titanic):
    c = Column('Age')
    assert str(c) == 'Age'

    c = Column()
    assert str(c) == '?'

    c = Column(hint=Hint(['papers']))
    assert str(c) == '?[papers]'

    c = Column(hint=Hint([['papers', '10']]))
    assert str(c) == '?[papers, 10]'

    c = Column(titanic['Age'])
    assert str(c) == 'titanic.Age'


def test_table_basic(titanic):
    t = Table('Tb')
    assert str(t) == 'Tb'

    t = Table()
    assert str(t) == '??'

    t = Table(hint=Hint(['unique']))
    assert str(t) == '??[unique]'

    t = Table(titanic)
    assert str(t) == 'titanic'


def test_aggregate_basic():
    c = Column('Age')
    for f in ops.all_aggregates:
        e = f(c)
        assert str(e) == f'{e.func}({c})'

    c = Column(hint=Hint(['papers', '10']))
    for f in ops.all_aggregates:
        e = f(c)
        assert str(e) == f'{e.func}({c})'


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





