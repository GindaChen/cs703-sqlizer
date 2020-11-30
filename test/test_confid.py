from query.base import Hint
from query.expr import AbstractColumns, Value, Column, \
    Table, Predicate, Projection, Selection, Join
from database.table import popDatabase
import query.operators as ops
from test.db import getForeignDB, getTinyDB


def test_JoinConfid():
    getForeignDB()

    p = Projection(
        Join(Table(hint=Hint("author")), Table(hint=Hint("papers")), lhs_col=Column(hint=Hint()), rhs_col=Column(hint=Hint())),
        AbstractColumns(Column(hint=Hint("id")))
    )

    sc_list = p.getCandidates()
    res = [p.unparse(sketch_compl=sc) for sc in sc_list]
    assert len(res) == 6 * 6
    assert "SELECT author.id\nFROM author JOIN papers ON author.name = papers.title" in res
    assert "SELECT author.id\nFROM author JOIN papers ON author.name = papers.author_name" == res[0]

    popDatabase()


# similar to test_inferValue, but check confidence
def test_CastConfid():
    getTinyDB()

    s = Selection(Table(hint=Hint("author")),
        Predicate(ops.ge, Column(hint=Hint()), Value("Loris")))
    ps = Projection(s, AbstractColumns(c=Column(hint=Hint("id"))))
    sc_list = ps.getCandidates()
    res = [ps.unparse(sketch_compl=sc) for sc in sc_list]

    assert len(res) == 3 * 3
    assert "SELECT author.id\nFROM author\nWHERE (author.id >= Loris)" in res
    assert "SELECT author.name\nFROM author\nWHERE (author.name >= \"Loris\")" in res
    assert "SELECT author.id\nFROM author\nWHERE (author.name >= \"Loris\")" == res[0]

    popDatabase()
