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

    db.add_table("t1")
    db.add_table("t2")

    t1 = db["t1"]
    t2 = db["t2"]
    t1.add_column("c1n", numeric)
    t1.add_column("c1s", string)
    t1.add_column("c1b", boolean)
    t2.add_column("c2n", numeric)
    t2.add_column("c2s", string)
    t2.add_column("c2s_", string, foreign_of=t1["c1s"])
    
    return db

def getTinyDB():
    pushDatabase("db_test_tiny")
    db = getDatabase()

    db.add_table("t1")

    t1 = db["t1"]
    t1.add_column("c1n", numeric)
    t1.add_column("c1s", string)
    t1.add_column("c1b", boolean)

    return db


def test_JoinConfid():
    getForeignDB()

    p = Projection(
        Join(Table(hint=Hint("t1")), Table(hint=Hint("t2")), lhs_col=Column(hint=Hint("c1s")), rhs_col=Column(hint=Hint("c2s"))),
        AbstractColumns(Column(hint=Hint("c1n")))
    )

    sc_list = p.getCandidates();
    res = [p.unparse(sketch_compl=sc) for sc in sc_list]
    assert len(res) == 6 * 6
    assert "SELECT t1.c1n\nFROM t1 JOIN t2 ON t1.c1s = t2.c2s" in res
    assert "SELECT t1.c1n\nFROM t1 JOIN t2 ON t1.c1s = t2.c2s_" in res[:12]

    popDatabase()


# similar to test_inferValue, but check confidence
def test_CastConfid():
    getTinyDB()

    s = Selection(Table(hint=Hint("t1")),
        Predicate(ops.ge, Column(hint=Hint("c1")), Value("2010")) )
    ps = Projection(s, AbstractColumns(c=Column(hint=Hint("c1n"))))
    sc_list = ps.getCandidates()
    res = [ps.unparse(sketch_compl=sc) for sc in sc_list]

    for r in res:
        print(r)


    assert len(res) == 3 * 3
    assert "SELECT t1.c1n\nFROM t1\nWHERE (t1.c1n >= 2010)" in res
    assert "SELECT t1.c1s\nFROM t1\nWHERE (t1.c1s >= \"2010\")" in res
    assert "SELECT t1.c1n\nFROM t1\nWHERE (t1.c1s >= \"2010\")" == res[0]

    popDatabase()
