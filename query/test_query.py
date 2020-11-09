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
    pass



