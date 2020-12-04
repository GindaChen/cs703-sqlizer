from database.engine import LoadDatabase, CloseDatabase
from main import substitute, synthesis
from query import operators
from query.base import Hint
from query.expr import Projection, Selection, Table, Predicate, Column, Value, AbstractColumns, Join, Aggregation
from test.test_engine import buildTestMASDatabaseIfNotExist


def test_substitute():
    j = Join(
        lhs_abs_table=Table(hint=Hint("papers")),
        rhs_abs_table=Table(hint=Hint()),
        lhs_col=Column(hint=Hint()),
        rhs_col=Column(hint=Hint()),
    )

    t = Table(hint=Hint("test"))

    p = Projection(
        Selection(j, Predicate(operators.eq, Column(hint=Hint()), Value("OOPSLA 2010"))),
        AbstractColumns(Column(hint=Hint("papers")))
    )

    expected = Projection(
        Selection(t, Predicate(operators.eq, Column(hint=Hint()), Value("OOPSLA 2010"))),
        AbstractColumns(Column(hint=Hint("papers")))
    )

    actual = substitute(p, j, t)
    assert expected.unparse() == actual.unparse()


def test_synthesis():
    buildTestMASDatabaseIfNotExist()
    LoadDatabase("test_mas.db")

    p = Projection(
        Selection(
            Table(hint=Hint("papers")),
            Predicate(operators.eq, Column(hint=Hint()), Value("OOPSLA 2010"))
        ),
        AbstractColumns(
            Aggregation(operators.count_, Column(hint=Hint("papers")))
        )
    )
    sketches = synthesis(p)

    res = [s.expr.unparse(sketch_compl=s) for s in sketches]

    assert 'SELECT count(Publication.abstract)\nFROM Publication JOIN Conference ON Publication.cid = Conference.cid\nWHERE ((Conference.name = "OOPSLA") AND (Publication.year = 2010))' in res
    assert 'SELECT count(Publication.abstract)\nFROM Conference JOIN Publication ON Conference.cid = Publication.cid\nWHERE ((Conference.name = "OOPSLA") AND (Publication.year = 2010))' in res

    CloseDatabase()
