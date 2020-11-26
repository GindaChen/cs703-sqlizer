from query import operators
from query.base import Hint
from query.expr import Predicate, Column, Value, Selection, Table, Projection, AbstractColumns
from query.repair import add_pred, add_join1, add_join2, add_func


def test_add_pred():
    p = Predicate(operators.eq, Column(hint=Hint()), Value("OOPSLA"))
    candidates = add_pred(p)
    assert len(candidates) is len("OOPSLA") - 1

    res = [c.unparse() for c in candidates]

    assert '((? = "O") AND (? = "OPSLA"))' in res
    assert '((? = "OOPSL") AND (? = "A"))' in res


def test_add_join1():
    p = Selection(Table(hint=Hint("papers")), Predicate(operators.eq, Column("year"), Value(2010)))
    candidates = add_join1(p)
    assert len(candidates) is 1

    candidate = candidates[0]
    assert candidate.unparse() == "??[papers] JOIN ?? ON ? = ?\nWHERE (year = 2010)"


def test_add_join2():
    p = Projection(
        Table("Publication"),
        AbstractColumns(from_list=[Column("title"), Column("homepage")])
    )
    candidates = add_join2(p)
    assert len(candidates) is 1

    candidate = candidates[0]
    assert candidate.unparse() == "SELECT title, homepage\nFROM Publication JOIN ?? ON ? = ?"


def test_add_func():
    c = Column(hint=Hint("max grade"))
    candidates = add_func(c)
    assert len(candidates) is 1

    candidate = candidates[0]
    assert candidate.unparse() == "max(?[grade])"
