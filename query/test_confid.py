from query.base import Hint
from query.infer import TypeCheck, SingleSketchCompl, ComposeSketchCompl
from query.expr import Entity, AbstractTable, AbstractColumns, Value, Column, \
    Table, GroupAgg, Aggregation, Predicate, Projection, Selection, Join
from query.confid import BaseConfid, HintConfid, JoinConfid, PredConfid
from database.table import pushDatabase, popDatabase, getDatabase, DatabaseColumn, DatabaseTable
from query.type import boolean, numeric, string
import query.operators as ops
import query.params as params


def getForeignDB():
    pushDatabase("db_test_foreign")
    db = getDatabase()

    db.add_table("author")
    db.add_table("papers")

    t1 = db["author"]
    t2 = db["papers"]
    t1.add_column("id", numeric)
    t1.add_column("name", string)
    t1.add_column("is_student", boolean)
    t2.add_column("pages", numeric)
    t2.add_column("title", string)
    t2.add_column("author_name", string, foreign_of=t1["name"])
    
    return db

def getTinyDB():
    pushDatabase("db_test_tiny")
    db = getDatabase()

    db.add_table("author")

    t1 = db["author"]
    t1.add_column("id", numeric)
    t1.add_column("name", string)
    t1.add_column("is_student", boolean)

    return db


def test_JoinConfid():
    getForeignDB()

    p = Projection(
        Join(Table(hint=Hint("author")), Table(hint=Hint("papers")), lhs_col=Column(hint=Hint("_")), rhs_col=Column(hint=Hint("_"))),
        AbstractColumns(Column(hint=Hint("id")))
    )

    sc_list = p.getCandidates();
    res = [p.unparse(sketch_compl=sc) for sc in sc_list]
    assert len(res) == 6 * 6
    assert "SELECT author.id\nFROM author JOIN papers ON author.name = papers.title" in res
    # assert "SELECT author.id\nFROM author JOIN papers ON author.name = papers.author_name" in res[:12]

    popDatabase()


# similar to test_inferValue, but check confidence
def test_CastConfid():
    getTinyDB()

    s = Selection(Table(hint=Hint("author")),
        Predicate(ops.ge, Column(hint=Hint("_")), Value("Loris")) )
    ps = Projection(s, AbstractColumns(c=Column(hint=Hint("id"))))
    sc_list = ps.getCandidates()
    res = [ps.unparse(sketch_compl=sc) for sc in sc_list]

    assert len(res) == 3 * 3
    assert "SELECT author.id\nFROM author\nWHERE (author.id >= Loris)" in res
    assert "SELECT author.name\nFROM author\nWHERE (author.name >= \"Loris\")" in res
    # assert "SELECT author.id\nFROM author\nWHERE (author.name >= \"Loris\")" == res[0] # require w2c works

    popDatabase()
