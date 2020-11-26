
from query.base import Hint
from query.infer import TypeCheck, SingleSketchCompl, ComposeSketchCompl
from query.expr import Entity, AbstractTable, AbstractColumns, Value, Column, \
    Table, GroupAgg, Aggregation, Predicate, Projection, Selection, Join
from query.confid import BaseConfid, HintConfid, JoinConfid, PredConfid
from database.table import pushDatabase, popDatabase, getDatabase, DatabaseColumn, DatabaseTable
from query.type import boolean, numeric, string
import query.operators as ops


def get_mas_db():
    """Get the mas database in paper"""
    pushDatabase("db_test_mas")

    db = getDatabase()

    db.add_table("publication")
    publication = db["publication"]
    publication.add_column("pid", numeric)
    publication.add_column("title", string)
    publication.add_column("abstract", string)
    publication.add_column("year", numeric)
    publication.add_column("cid", numeric)
    publication.add_column("jid", numeric)

    db.add_table("author")
    author = db["author"]
    author.add_column("aid", numeric)
    author.add_column("name", string)
    author.add_column("homepage", string)

    db.add_table("writes")
    writes = db["writes"]
    writes.add_column("aid", numeric)
    writes.add_column("pid", numeric)


def getSimpleDB():
    pushDatabase("db_test_simple")
    db = getDatabase()

    db.add_table("t1")
    db.add_table("t2")

    t1 = db["t1"]
    t2 = db["t2"]
    t1.add_column("c11", numeric)
    t1.add_column("c12", string)
    t1.add_column("c13", boolean)
    t2.add_column("c21", numeric)
    t2.add_column("c22", string)
    return db


def test_hint_confid():
    get_mas_db()
    t = Table(hint=Hint("papers"))
    sc_list = t.getCandidates()
    res = {t.unparse(sketch_compl=sc) : sc.confid for sc in sc_list}
    assert res["writes"] > res["publication"] > res["author"]
    # the model thinks that `papers` is more similar to `writes` than to `publication` for some reason
    popDatabase()


def test_inferTable():
    getSimpleDB()
    t = Table(hint=Hint("t_hint_1"))
    sc_list = t.getCandidates()
    res = [t.unparse(sketch_compl=sc) for sc in sc_list]
    assert len(res) == 2
    assert "t1" in res
    assert "t2" in res
    popDatabase()


# the assertion for len(res) might change depending on the optimization applied to infer
def test_inferAbstractTable():
    getSimpleDB()

    p = Projection(Table(hint=Hint("t_hint_1")),
        AbstractColumns(from_list=[Column(hint=Hint("c_hint_1")), Column(hint=Hint("c_hint_2"))]))
    sc_list = p.getCandidates()
    res = [p.unparse(sketch_compl=sc) for sc in sc_list]
    assert len(res) == 6 + 2
    assert "SELECT t1.c13, t1.c12\nFROM t1" in res
    assert "SELECT t2.c21, t2.c22\nFROM t2" in res
    assert "SELECT t1.c13, t1.c12\nFROM t2" not in res
    assert "SELECT t1.c12, t2.c12\nFROM t1" not in res

    pp = Projection(p, AbstractColumns(Column(hint=Hint("c_hint_3"))))
    sc_list = pp.getCandidates()
    res = [pp.unparse(sketch_compl=sc) for sc in sc_list]
    assert len(res) == (6 * 2) + (2 * 2)
    assert "SELECT t1.c13\nFROM (SELECT t1.c13, t1.c12\n\tFROM t1)" in res
    assert "SELECT t2.c21\nFROM (SELECT t1.c13, t1.c12\n\tFROM t1)" not in res

    sp = Selection(p, Predicate(ops.eq, Column(hint=Hint("c_hint_4")), Value(2010)))
    psp = Projection(sp, AbstractColumns(Column(hint=Hint("c_hint_5"))))
    sc_list = psp.getCandidates()
    res = [psp.unparse(sketch_compl=sc) for sc in sc_list]
    assert len(res) == (6 * 2 * 2) + (2 * 2 * 2)
    assert "SELECT t1.c12\nFROM (SELECT t1.c11, t1.c12\n\tFROM t1)\nWHERE (t1.c12 = 2010)" in res
    assert "SELECT t1.c12\nFROM (SELECT t1.c11, t1.c12\n\tFROM t1)\nWHERE (t1.c13 = 2010)" not in res

    j = Join(
        Table(hint=Hint("t_hint_2")),
        Table(hint=Hint("t_hint_3")),
        Column(hint=Hint("t_hint_6")),
        Column(hint=Hint("t_hint_7"))
    )
    psj = Projection(
        Selection(j, Predicate(ops.eq, Column(hint=Hint("c_hint_8")), Value(2010))),
        AbstractColumns(from_list=[Column(hint=Hint("c_hint_9")), Column(hint=Hint("c_hint_10"))]))
    sc_list = psj.getCandidates()
    res = [psj.unparse(sketch_compl=sc) for sc in sc_list]
    assert len(res) == 2 * (20 * 2 * 5)
    assert "SELECT t2.c21, t1.c12\nFROM t1 JOIN t2 ON t1.c12 = t2.c22\nWHERE (t1.c13 = 2010)" in res
    assert "SELECT t2.c21, t1.c12\nFROM t1 JOIN t2 ON t1.c12 = t2.c21\nWHERE (t1.c13 = 2010)" not in res
    assert "SELECT t2.c21, t1.c12\nFROM t1 JOIN t2 ON t2.c22 = t1.c12\nWHERE (t1.c13 = 2010)" not in res

    popDatabase()

def test_inferGroupAgg():
    getSimpleDB()

    a = Aggregation(ops.max_, Column(hint=Hint("c_hint_1")))
    g = GroupAgg(a, Column(hint=Hint("c_hint_2")))
    pg = Projection(
        Table(hint=Hint("t_hint_1")),
        AbstractColumns(from_list=[g, Column(hint=Hint("c_hint_3"))]))
    sc_list= pg.getCandidates()
    res = [pg.unparse(sketch_compl=sc) for sc in sc_list]
    assert len(res) == 1 * 3 * 3 + 1 * 2 * 2
    assert "SELECT max(t1.c11), t1.c12\nFROM t1\nGROUP BY t1.c13" in res
    assert "SELECT max(t1.c11), t1.c12\nFROM t1\nGROUP BY t2.c21" not in res
    assert "SELECT max(t1.c13), t1.c12\nFROM t1\nGROUP BY t1.c13" not in res

    popDatabase()
