from query.expr import Column
from query.operators import max_, min_


def test_aggregate_basic():
    c = Column('Age')

    e = max_(c)
    assert str(e) == f'max({c.value})'

    e = min_(c)
    assert str(e) == f'min({c.value})'


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


