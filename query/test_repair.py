from query import operators
from query.base import Hint
from query.expr import Predicate, Column, Value, Selection, Table
from query.repair import add_pred, add_join1


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

    assert candidate.unparse() == "??[papers] JOIN ?? ON ? = ? \nWHERE (year = 2010)"
