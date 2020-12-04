from copy import deepcopy, copy

from database.engine import LoadDatabase, CloseDatabase
from query import operators
from query.base import Hint, BaseExpr
from query.expr import AbstractTable, Projection, Selection, Table, Predicate, Column, Value, AbstractColumns
from query.params import confid_threshold, top_k
from query.repair import fault_localize, repair_sketch
from test.test_engine import buildTestMASDatabaseIfNotExist


def substitute(query: AbstractTable, a: BaseExpr, b: BaseExpr) -> AbstractTable:
    """
    traverse the tree and substitute the matching subtree a to b

    a new copy is returned with `all_candidates` set to None
    """

    def copy_and_replace(curr, key, val):
        new_curr = copy(curr)
        setattr(new_curr, key, val)
        return new_curr

    def helper(curr):
        """
        return the changed child, or `None` if current node is not changed
        """
        if not isinstance(curr, BaseExpr):
            return None

        curr.all_candidates = None

        for k, v in vars(curr).items():
            if v == a:
                return copy_and_replace(curr, k, b)

            res = helper(v)
            if res:
                return copy_and_replace(curr, k, res)

        return None

    return helper(query)


# ~ algorithm 1
def synthesis(query: AbstractTable, depth=3):
    if depth == 0:
        return []

    print("=======================================")
    print("current query", repr(query.unparse()))

    sketches = query.getCandidates()
    confident_sketches = [s for s in sketches if s.confid.score > confid_threshold]
    if confident_sketches:
        return confident_sketches

    for sketch in sketches[:top_k]:
        print(sketch.confid, repr(query.unparse(sketch_compl=sketch)))
        res = fault_localize(query, sketch)
        if res is None:
            break
        expr, _ = res
        repaired_exprs = repair_sketch(expr)
        for repaired_expr in repaired_exprs:
            new_query = substitute(query, expr, repaired_expr)
            res = synthesis(new_query, depth - 1)
            if res:
                return res


def main():
    buildTestMASDatabaseIfNotExist()
    LoadDatabase("test_mas.db")

    p = Projection(
        Selection(
            Table(hint=Hint("papers")),
            Predicate(operators.eq, Column(hint=Hint()), Value("OOPSLA 2010"))
        ),
        AbstractColumns(Column(hint=Hint("papers")))
    )
    synthesis(p)

    CloseDatabase()


if __name__ == '__main__':
    main()
