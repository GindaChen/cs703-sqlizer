# Repair tactics implementation
# Basically some modification to AST node
from query import operators
from query.base import BaseExpr
from query.expr import Entity, AbstractTable, AbstractColumns, Value, Column, Table, GroupAgg, Aggregation, Predicate, \
    Projection, Selection, Join

from query.type import string


def add_pred(pred_expr: Predicate):
    repairs = []

    func = pred_expr.func
    lhs = pred_expr.args[0]
    rhs = pred_expr.args[1]

    if func.arity is not 2:
        return repairs

    if isinstance(rhs, Value) and rhs.type is string:
        str_val = rhs.val
        for i in range(1, len(str_val)):
            p1 = Predicate(func, lhs, Value(str_val[:i]))
            p2 = Predicate(func, lhs, Value(str_val[i:]))
            p = Predicate(operators.and_, p1, p2)
            repairs.append(p)

    return repairs


def repair_sketch(subpart: BaseExpr):
    repairs = []
    if isinstance(subpart, Predicate):
        repairs += add_pred(subpart)
