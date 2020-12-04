from main import substitute
from query import operators
from query.base import Hint
from query.expr import Projection, Selection, Table, Predicate, Column, Value, AbstractColumns, Join


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
