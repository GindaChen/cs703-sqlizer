# Repair tactics implementation
# Basically some modification to AST node
from typing import List

from query import operators
from query.base import BaseExpr, Hint
from query.expr import Value, Column, Table, GroupAgg, Aggregation, Predicate, Projection, Selection, Join
from query.infer import ComposeSketchCompl, TypeCheck
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
        indices = [i for i, c in enumerate(str_val) if not c.isalnum()]

        for i in indices:
            p1 = Predicate(func, lhs, Value(str_val[:i]))
            p2 = Predicate(func, lhs, Value(str_val[i + 1:]))
            p = Predicate(operators.and_, p1, p2)  # TODO: we only consider two-way split for now
            repairs.append(p)

        # for i in range(1, len(str_val)):
        #     p1 = Predicate(func, lhs, Value(str_val[:i]))
        #     p2 = Predicate(func, lhs, Value(str_val[i:]))
        #     p = Predicate(operators.and_, p1, p2)
        #     repairs.append(p)

    return repairs


def add_join1(selection_expr: Selection):
    j = Join(
        selection_expr.abs_table,
        Table(hint=Hint()),
        Column(hint=Hint()),
        Column(hint=Hint())
    )

    s = Selection(j, selection_expr.pred)

    return [s]


def add_join2(projection_expr: Projection):
    j = Join(
        projection_expr.abs_table,
        Table(hint=Hint()),
        Column(hint=Hint()),
        Column(hint=Hint())
    )

    s = Projection(j, projection_expr.abs_cols)

    return [s]


def add_join3(join_expr: Join):
    # TODO: The hint seems to be discarded in this repair tactic from the original paper. Can we do better?

    j1 = Join(
        join_expr.lhs_abs_table,
        Table(hint=Hint()),
        Column(hint=Hint()),
        Column(hint=Hint())
    )

    j2 = Join(
        j1,
        join_expr.rhs_abs_table,
        Column(hint=Hint()),
        Column(hint=Hint())
    )

    return [j2]


def add_func(column: Column):
    if column.hint is None:
        return []

    repairs = []

    for h in column.hint:
        maybe_func, new_hint = h.split(maxsplit=1)
        for f in all_aggregates:
            if f.name == maybe_func:  # TODO: replace with word similarity
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


def repair_sketch(expr: BaseExpr):
    repairs = []
    if isinstance(expr, Predicate):
        repairs += add_pred(expr)
    if isinstance(expr, Selection):
        repairs += add_join1(expr)
    if isinstance(expr, Projection):
        repairs += add_join2(expr)
    if isinstance(expr, Join):
        repairs += add_join3(expr)
    if isinstance(expr, Predicate):
        repairs += add_col(expr)
    if isinstance(expr, Column):
        repairs += add_func(expr)
    return repairs


def can_repair(expr: BaseExpr):
    return len(repair_sketch(expr)) != 0


def get_sub_relations(expr: BaseExpr, sketch: ComposeSketchCompl):
    if isinstance(expr, Selection):
        return [(expr.abs_table, expr.pred, sketch.getSubCompl(0), sketch.getSubCompl(1))]
    if isinstance(expr, Projection):
        return [(expr.abs_table, expr.abs_cols, sketch.getSubCompl(0), sketch.getSubCompl(1))]
    if isinstance(expr, Join):
        return [
            (expr.rhs_abs_table, expr.rhs_col, sketch.getSubCompl(0), sketch.getSubCompl(2)),
            (expr.lhs_abs_table, expr.lhs_col, sketch.getSubCompl(1), sketch.getSubCompl(3)),
        ]


def get_sub_specifiers(expr: BaseExpr):
    if isinstance(expr, Predicate):
        return list(expr.args)
    if isinstance(expr, GroupAgg):
        return [expr.agg.col, expr.by_col]


def fault_localize(expr: BaseExpr, sketch: ComposeSketchCompl):
    # line 4: if expr is a relation
    if any(isinstance(expr, cls) for cls in [Selection, Projection, Join]):

        # line 5
        sub_relations = get_sub_relations(expr, sketch)
        for relation, specifier, relation_sketch, specifier_sketch in sub_relations:

            # line 6 - 7
            specifier_2, specifier_sketch_2 = fault_localize(relation, relation_sketch)
            if specifier_2 is not None:
                return specifier_2, specifier_sketch_2

            # line 8 - 10
            omega = [fault_localize(relation, s) for s in relation.infer()]

            # line 11: the specifier is faulty if its faulty for all possible inhabitants
            if all(e for e in omega):
                if len(set(omega)) == 1:
                    return omega[0]
                elif can_repair(specifier):
                    return specifier, specifier_sketch

    # line 14 - 17: if expr is a specifier, we recurse down to its sub_specifiers
    elif any(isinstance(expr, cls) for cls in [Predicate, GroupAgg]):
        sub_specifiers = get_sub_specifiers(expr)
        for specifier in sub_specifiers:
            omega, sub_sketch = fault_localize(specifier, sketch)
            if omega:
                return omega, sub_sketch

    # line 18: we consider the current sketch as the possible cause of failure
    sub_sketches = expr.infer()
    if max(s.confid.score for s in sub_sketches) < 1 and can_repair(expr):
        return expr, sketch

    return None
