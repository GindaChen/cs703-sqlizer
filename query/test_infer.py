
from query.infer import SketchCompl, inferTable
from query.expr import Entity, AbstractTable, AbstractColumns, Value, Column, \
    Table, GroupAgg, Aggregation, Predicate, Projection, Selection, Join
from query.confid import BaseConfid, HintConfid, JoinConfid, PredConfid
from database.table import db, Database

def test_inferTable():
    old_db = db
    db = Database("test_inferTable_db")
    db.add_column("test_col1")
    # TODO: finish word2vec so this test could work

    db = old_db # restore

