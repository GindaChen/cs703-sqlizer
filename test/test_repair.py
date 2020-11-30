from database.table import popDatabase
from query import operators
from query.base import Hint
from query.expr import Predicate, Column, Value, Selection, Table, Projection, AbstractColumns, Join
from query.repair import add_pred, add_join1, add_join2, add_func, add_col, add_join3, fault_localize
from test.db import getForeignDB, get_mas_db


def test_add_pred():
    p = Predicate(operators.eq, Column(hint=Hint()), Value("TEST OOPSLA 2020"))
    candidates = add_pred(p)
    assert len(candidates) is 2

    res = [c.unparse() for c in candidates]

    assert '((? = "TEST") AND (? = "OOPSLA 2020"))' in res
    assert '((? = "TEST OOPSLA") AND (? = "2020"))' in res


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


def test_add_join3():
    j = Join(
        Table("TableA"),
        Table("TableB"),
        Column(hint=Hint("col1")),
        Column(hint=Hint("col2")),
    )
    candidates = add_join3(j)
    assert len(candidates) is 1

    candidate = candidates[0]
    assert candidate.unparse() == "TableA JOIN ?? ON ? = ? JOIN TableB ON ? = ?"


def test_add_func():
    c = Column(hint=Hint("max grade"))
    candidates = add_func(c)
    assert len(candidates) is 1

    candidate = candidates[0]
    assert candidate.unparse() == "max(?[grade])"


def test_add_col():
    p = Predicate(operators.eq, Column(hint=Hint("Col1")), Value("Col2"))
    candidates = add_col(p)
    assert len(candidates) is 1

    candidate = candidates[0]
    assert candidate.unparse() == "(?[Col1] = ?[Col2])"


def test_fault_localize1():
    getForeignDB()

    expr = Projection(
        Join(
            Table(hint=Hint("author")),
            Table(hint=Hint("papers")),
            lhs_col=Column(hint=Hint()),
            rhs_col=Column(hint=Hint()),
        ),
        AbstractColumns(Column(hint=Hint("id")))
    )

    sc_list = expr.getCandidates()

    faulty_sketch = sc_list[0]

    assert expr.unparse(sketch_compl=faulty_sketch) == \
           'SELECT author.id\nFROM author JOIN papers ON author.name = papers.author_name'

    faulty_sub_expr, _ = fault_localize(expr, faulty_sketch)

    assert faulty_sub_expr.unparse() == '??[author] JOIN ??[papers] ON ? = ?'

    popDatabase()

# This test needs to work when we can access the database content.
# def test_fault_localize2():
#     get_mas_db()
#
#     p = Projection(
#         Selection(
#             Table(hint=Hint("papers")),
#             Predicate(operators.eq, Column(hint=Hint()), Value("OOPSLA 2010"))
#         ),
#         AbstractColumns(Column(hint=Hint("papers")))
#     )
#     assert p.unparse() == 'SELECT ?[papers]\nFROM ??[papers]\nWHERE (? = "OOPSLA 2010")'
#
#     sc_list = p.getCandidates()
#     sketch = sc_list[0]
#
#     expr, _ = fault_localize(p, sketch)
#
#     fault_localize(expr, sketch)
#
#     assert expr.unparse() == '??[papers]\nWHERE (? = "OOPSLA 2010")'
#
#     popDatabase()
