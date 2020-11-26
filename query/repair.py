# Repair tactics implementation
# Basically some modification to AST node
from query import operators
from query.base import BaseExpr, Hint
from query.expr import Entity, AbstractTable, AbstractColumns, Value, Column, Table, GroupAgg, Aggregation, Predicate, \
    Projection, Selection, Join
from query.operators import all_aggregates

from query.type import string


def add_pred(pred_expr: Predicate):
    repairs = []

    func = pred_expr.func
    if func.arity is not 2:
        return []

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


def add_join2(projection_expr: Projection):
    j = Join(
        projection_expr.abs_table,
        Table(hint=Hint()),
        AbstractColumns(Column(hint=Hint())),
        AbstractColumns(Column(hint=Hint()))
    )

    s = Projection(j, projection_expr.abs_cols)

    return [s]


def add_join3(join_expr: Join):
    # TODO: The hint seems to be discarded in this repair tactic from the original paper. Can we do better?

    j1 = Join(
        join_expr.lhs_abs_table,
        Table(hint=Hint()),
        AbstractColumns(Column(hint=Hint())),
        AbstractColumns(Column(hint=Hint()))
    )

    j2 = Join(
        j1,
        join_expr.rhs_abs_table,
        AbstractColumns(Column(hint=Hint())),
        AbstractColumns(Column(hint=Hint()))
    )

    return [j2]


def add_func(column: Column):
    if column.hint is None:
        return []

    repairs = []

    for h in column.hint:
        maybe_func, new_hint = h.split(maxsplit=1)
        for f in all_aggregates:
            if f.name == maybe_func: # TODO: replace with word similarity
                repairs += [Aggregation(f, Column(hint=Hint(new_hint)))]

    return repairs


def add_col(pred_expr: Predicate):
    if pred_expr.func.arity is not 2:
        return []

    lhs = pred_expr.args[0]
    rhs = pred_expr.args[1]

    if isinstance(lhs, Column) and isinstance(rhs, Value) and rhs.type is string:
        return [Predicate(pred_expr.func, lhs, Column(hint=Hint(rhs.val)))]

    return []


def repair_sketch(subpart: BaseExpr):
    repairs = []
    if isinstance(subpart, Predicate):
        repairs += add_pred(subpart)
    if isinstance(subpart, Selection):
        repairs += add_join1(subpart)
    if isinstance(subpart, Projection):
        repairs += add_join2(subpart)
    if isinstance(subpart, Join):
        repairs += add_join3(subpart)
    if isinstance(subpart, Predicate):
        repairs += add_col(subpart)
    if isinstance(subpart, Column):
        repairs += add_func(subpart)
