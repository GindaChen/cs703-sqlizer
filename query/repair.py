# Repair tactics implementation
# Basically some modification to AST node
from typing import List, Tuple, Union, Optional

from query import operators, params
from query.base import BaseExpr, Hint
from query.expr import Value, Column, Table, GroupAgg, Aggregation, Predicate, Projection, Selection, Join
from query.infer import ComposeSketchCompl, TypeCheck
from query.operators import all_aggregates
from query.type import string


def add_pred(pred_expr: Predicate):
    repairs = []

    func = pred_expr.func
    if func.arity != 2:
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
        splitted = h.split(maxsplit=1)
        if len(splitted) != 2:
            continue
        maybe_func, new_hint = splitted
        for f in all_aggregates:
            if f.name == maybe_func:  # TODO: replace with word similarity
                repairs += [Aggregation(f, Column(hint=Hint(new_hint)))]

    return repairs


def add_col(pred_expr: Predicate):
    if pred_expr.func.arity != 2:
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


def get_sub_relations(sketch: ComposeSketchCompl):
    expr = sketch.expr
    if isinstance(expr, Selection):
        return [(sketch.getSubCompl(0), sketch.getSubCompl(1))]
    if isinstance(expr, Projection):
        return [(sketch.getSubCompl(0), sketch.getSubCompl(1))]
    if isinstance(expr, Join):
        return [
            (sketch.getSubCompl(0), sketch.getSubCompl(2)),
            (sketch.getSubCompl(1), sketch.getSubCompl(3)),
        ]


def get_sub_specifiers(expr: BaseExpr):
    if isinstance(expr, Predicate):
        return list(expr.args)
    if isinstance(expr, GroupAgg):
        return [expr.agg.col, expr.by_col]


def fault_localize(sketch_compl: ComposeSketchCompl, sketch: BaseExpr = None) -> Optional[BaseExpr]:
    if sketch is None:
        sketch = sketch_compl.expr

    # line 4: if expr is a relation
    if isinstance(sketch, (Selection, Projection, Join)):

        # line 5
        sub_relations = get_sub_relations(sketch_compl)
        for sub_relation_compl, sub_specifier_compl in sub_relations:

            # line 6 - 7
            faulty_sub_sketch = fault_localize(sub_relation_compl)
            if faulty_sub_sketch is not None:
                return faulty_sub_sketch

            # line 8: `getCandidates` is called `FindInhabitants` in the algorithm
            candidates = sub_relation_compl.expr.getCandidates()
            # line 9 - 10
            omega = [fault_localize(s, sub_specifier_compl.expr) for s in candidates]

            # line 11: the specifier is faulty if its faulty for all possible inhabitants
            if all(e is not None for e in omega):
                if len(set(omega)) == 1:
                    return omega[0]
                elif can_repair(sub_specifier_compl.expr):
                    return sub_specifier_compl.expr

    # line 14 - 17: if expr is a specifier, we recurse down to its sub_specifiers
    elif isinstance(sketch, (Predicate, GroupAgg)):
        sub_specifiers = get_sub_specifiers(sketch)
        for sub_specifier in sub_specifiers:
            faulty_sub_sketch = fault_localize(sketch_compl, sub_specifier)
            if faulty_sub_sketch is not None:
                return faulty_sub_sketch

    # line 18: we consider the current sketch as the possible cause of failure
    sub_sketches = sketch.getCandidates(
        type_check=None if isinstance(sketch, (Selection, Projection, Join, Table)) else sketch_compl.type_check
    )

    if (
        max((s.confid.score for s in sub_sketches), default=-1) < params.confid_threshold and
        can_repair(sketch)
    ):
        return sketch

    return None
