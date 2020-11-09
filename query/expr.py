"""
Extended Relational Algebra
    Table   :=  Proj(Columns, Table)
            |   Selection(Predicate, Table)
            |   Join(Table_1, Table_2)
            |   t
    Columns := Columns.extends(Columns)
            | c
            | agg(c, *Columns) # == Aggregation(agg_column, *group_by_columns)
    Predicate := lop(*Predicate) # length varies among logical operations
                | op(c, Entity)  # Consider only binary operators
    Entity  := Table | c | v
    t := <table name>
    c := <column name>
    v := <value>
    agg := <aggregate functions>
    lop := and | or | neg
    op  := < | <= | > | >= | =
"""
from typing import List, Union

from query.base import BaseExpr


class Table(BaseExpr):
    def __init__(self, value):
        self.value = value


class Column(BaseExpr):
    def __init__(self, col):
        self.value = col


class Aggregation(BaseExpr):
    def __init__(self, func, col, group_by=None):
        self.func = func
        self.col = col
        self.group_by = group_by


class Predicate(BaseExpr):
    def __init__(self, func, *args):
        self.func = func
        self.args = args


class Projection(BaseExpr):
    def __init__(self, table: Table, project_expr):
        self.table = table
        self.expr = project_expr


class Selection(BaseExpr):
    def __init__(self, table: Table, select_expr: List[Column]):
        self.table = table
        self.expr = select_expr


class Join(BaseExpr):
    def __init__(self, lhs_table: Table, rhs_table: Table,
                 predicates: List[Predicate]):
        self.lhs = lhs_table
        self.rhs = rhs_table
        self.on = predicates
