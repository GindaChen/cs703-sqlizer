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
