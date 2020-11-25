from query import operators
from query.base import Hint
from query.expr import Predicate, Column, Value
from query.repair import add_pred


def test_add_pred():
    p = Predicate(operators.eq, Column(hint=Hint()), Value("OOPSLA"))
    candidates = add_pred(p)
    assert len(candidates) is len("OOPSLA") - 1

    res = [c.unparse() for c in candidates]

    assert '((? = "O") AND (? = "OPSLA"))' in res
    assert '((? = "OOPSL") AND (? = "A"))' in res
