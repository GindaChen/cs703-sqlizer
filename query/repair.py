# Repair tactics implementation
# Basically some modification to AST node
from query import operators
from query.base import BaseExpr, Hint
from query.expr import Entity, AbstractTable, AbstractColumns, Value, Column, Table, GroupAgg, Aggregation, Predicate, \
    Projection, Selection, Join

from query.type import string


def add_pred(pred_expr: Predicate):
    repairs = []

    func = pred_expr.func
    if func.arity is not 2:
        return repairs

    lhs = pred_expr.args[0]
    rhs = pred_expr.args[1]

    if isinstance(lhs, Column) and isinstance(rhs, Value) and rhs.type is string:
        str_val = rhs.val
        for i in range(1, len(str_val)):
            p1 = Predicate(func, lhs, Value(str_val[:i]))
            p2 = Predicate(func, lhs, Value(str_val[i:]))
            p = Predicate(operators.and_, p1, p2)
            repairs.append(p)

    return repairs


def add_join1(selection_expr: Selection):
    j = Join(
        selection_expr.abs_table,
        Table(hint=Hint()),
        AbstractColumns(Column(hint=Hint())),
        AbstractColumns(Column(hint=Hint()))
    )

    s = Selection(j, selection_expr.pred)

    return [s]


def repair_sketch(subpart: BaseExpr):
    repairs = []
    if isinstance(subpart, Predicate):
        repairs += add_pred(subpart)
    if isinstance(subpart, Selection):
        repairs += add_join1(subpart)
