# Inference rules implementation
# Fig 7 and Fig 8

from query.base import BaseExpr, Hint
from query.expr import Entity, AbstractTable, AbstractColumns, Value, Column, \
    Table, GroupAgg, Aggregation, Predicate, Projection, Selection, Join
from query.confid import BaseConfid, HintConfid, JoinConfid, PredConfid
from database.table import db

def SketchCompl():
    # expr is the expression to complete
    # compl is a completion map Hint to the string to fill in
    def __init__(self, expr: BaseExpr, compl: dict, confid: BaseConfid):
        self.expr = expr
        self.compl = compl
        self.confid = confid
    
    def __str__(self):
        return f'-----\n{self.expr}\n{self.compl}\nConfidence: {self.confid}\n-----\n'
    
    def __lt__(self, other):
        return self.confid < other.confid

# The inference rules produce a list of completion sorted by confidence

def inferTable(table: Table):
    candidates = [SketchCompl(table, {table.hint: table_name}, HintConfid(table.hint, table_name))
        for table_name in db.getAllTableNames()]
    candidates.sort(reverse=True) # sorted by confid.
    return candidates


def inferSelection(sel: Selection):
    # TODO:
    pass


def inferProjection(proj: Projection):
    # TODO:
    pass


def inferJoin(join: Join):
    # TODO:
    pass

