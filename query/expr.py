"""
Extended Relational Algebra
    Table   :=  Proj(Columns, Table)
            |   Selection(Predicate, Table)
            |   Join(Table_1, Table_2)
            |   t
    Columns := Columns.extends(Columns)
            | [c]              # List of column
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
from typing import List

import query.operators as ops
from database.table import DatabaseColumn, DatabaseTable
from query.base import BaseExpr, AggregateFunc, Operator, Hint


class Column(BaseExpr):
    def __init__(self, col=None, type_=None, hint=None, table=None):
        super(Column, self).__init__()
        self.value = col
        self.type_ = type_
        self.table = table
        self.hint = Hint(hint=hint)

    @property
    def is_bound(self):
        return isinstance(self.value, DatabaseColumn)

    def __str__(self):
        hint = str(self.hint)
        cname = str(self.value) if self.value else '?'
        return f'{cname}{hint}'

    def __eq__(self, other):
        return Predicate(ops.eq, self, other)

    def __ne__(self, other):
        return Predicate(ops.neg, (self == other))

    def __gt__(self, other):
        return Predicate(ops.gt, self, other)

    def __ge__(self, other):
        return Predicate(ops.ge, self, other)

    def __lt__(self, other):
        return Predicate(ops.lt, self, other)

    def __le__(self, other):
        return Predicate(ops.le, self, other)


class Table(BaseExpr):
    def __init__(self, value=None, hint=None):
        super().__init__()
        self.value: List[Column] = value
        self.hint = Hint(hint=hint)
        self.columns = []

    @property
    def is_bound(self):
        return isinstance(self.value, DatabaseTable)

    def __str__(self):
        hint = str(self.hint)
        tname = str(self.value) if self.value else '??'
        return f'{tname}{hint}'

    def add_column(self, col=None, type_=None, hint=None) -> Column:
        c = Column(col=col, type_=type_, hint=hint, table=self)
        self.columns.append(c)
        return c


class Aggregation(BaseExpr):
    def __init__(self, func, col: Column, group_by=None):
        super().__init__()
        self.func: AggregateFunc = func
        self.col: Column = col
        self.group_by: List[Column] = group_by

    def __str__(self):
        # TODO: Can't just produce a SQL query from Aggregation...
        fn = self.func.name
        c = str(self.col)
        g = ", ".join([str(i) for i in self.group_by])
        agg = f'{fn}({c})'
        if not g:
            return agg
        return f'<{agg}, {g}>'


class Predicate(BaseExpr):
    def __init__(self, func, *args):
        super().__init__()
        self.func: Operator = func
        self.args = args

    def and_(self, other):
        return Predicate(ops.and_, self, other)

    def or_(self, other):
        return Predicate(ops.or_, self, other)

    def not_(self):
        return Predicate(ops.neg, self)

    def __str__(self):
        func = self.func.name
        arity = self.func.arity
        if arity == 1:
            v = self.args[0]
            return f'{func}({v})'
        elif arity == 2:
            lhs, rhs = (str(i) for i in self.args)
            return f'({lhs} {func} {rhs})'


class Projection(BaseExpr):
    def __init__(self, table: Table, project_expr):
        super().__init__()
        self.table = table
        self.expr = project_expr


class Selection(BaseExpr):
    def __init__(self, table: Table, select_expr: List[Column]):
        super().__init__()
        self.table = table
        self.expr = select_expr


class Join(BaseExpr):
    def __init__(self, lhs_table: Table, rhs_table: Table,
                 predicates: List[Predicate]):
        super().__init__()
        self.lhs = lhs_table
        self.rhs = rhs_table
        self.on = predicates


class QueryExpr():
    """SQL expression builder"""

    def __init__(self):
        self.from_ = []
        self.select = []
        self.where = []
        self.join = []
        self.group_by = []
        pass

    def run(self, root):
        pass

    def to_sql(self):
        pass

    def __str__(self):
        pass
