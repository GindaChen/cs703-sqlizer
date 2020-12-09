import time

from copy import copy
from typing import List

from database.engine import LoadDatabase, CloseDatabase
from query import operators
from query.base import Hint, BaseExpr
from query.expr import AbstractTable, Projection, Selection, Table, Predicate, Column, Value, AbstractColumns, \
    Aggregation
from query.infer import BaseSketchCompl
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
def synthesis(query: AbstractTable, depth=3) -> List[BaseSketchCompl]:
    if depth == 0:
        return []

    print("=======================================")
    print(f"current sketch: {repr(query.unparse())}")

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


def main_demo_mas():
    buildTestMASDatabaseIfNotExist()
    LoadDatabase("test_mas.db")

    p = Projection(
        Selection(
            Table(hint=Hint("papers")),
            Predicate(operators.eq, Column(hint=Hint()), Value("OOPSLA 2010"))
        ),
        AbstractColumns(
            Aggregation(operators.count_, Column(hint=Hint("papers")))
        )
    )

    start = time.time()
    res = synthesis(p)
    end = time.time()

    for r in res:
        print(r)

    print(f"synthesis takes {end - start}")

    CloseDatabase()

def yelp_q1():
    # # Query 1:
    # # Give me all the moroccan restaurants in Texas
    # # Sketch: 
    # #   - select:select(moroccan restaurant), where:location(Texas)
    sketches = []
    solution = "SELECT name FROM business JOIN category ON (business.bid = category.id) WHERE category.category_name = 'Moroccan';"
    print("Yelp Query 1: Give me all the moroccan restaurants in Texas")
    print(f"Yelp Query 1 Golden Solution: {solution}")
    

    p = Projection(
        Selection(
            Table(hint=Hint(["business"])),
            Predicate(operators.and_, 
                Predicate(operators.eq, Column(hint=Hint("state")), Value("Texas") ),
                Predicate(operators.eq, Column(hint=Hint("category_name")), Value("Moroccan"))
            )
        ),
        AbstractColumns(
            Column(hint=Hint(["name"]))
        )
    )
    sketches.append(p)

    # p = Projection(
    #     Selection(
    #         # Table(hint=Hint(["restaurant"])),
    #         Table(hint=Hint(["business"])),
    #         Predicate(operators.and_, 
    #             Predicate(operators.eq, Column(hint=Hint("State")), Value("Texas") ),
    #             Predicate(operators.eq, Column(hint=Hint("Category")), Value("Moroccan"))
    #         )
    #     ),
    #     AbstractColumns(
    #         Column(hint=Hint(["name"]))
    #     )
    # )
    # sketches.append(p)

    # p = Projection(
    #     Selection(
    #         Table(hint=Hint(["restaurant"])),
    #         Predicate(operators.eq, Column(hint=Hint("State")), Value("Texas") ),
    #         Predicate(operators.eq, Column(hint=Hint("Category")), Value("moroccan")),
    #     ),
    #     AbstractColumns(
    #         Column(hint=Hint(["restaurant"]))
    #     )
    # )
    # sketches.append(p)

    # p = Projection(
    #     Selection(
    #         Table(hint=Hint(["moroccan", "restaurant"])),
    #         Predicate(operators.eq, Column(hint=Hint("Place")), Value("Texas") ),
    #     ),
    #     AbstractColumns(
    #         Column(hint=Hint(["moroccan", "restaurant"]))
    #     )
    # )
    # sketches.append(p)

    return sketches

def main():
    db_path = "yelp.db"
    LoadDatabase(db_path)

    queries = [yelp_q1]
    for q in queries:
        sketches = q()
        for p in sketches:
            print(f"Initial Sketch: {p}")

            start = time.time()
            res = synthesis(p)
            end = time.time()

            for r in res:
                print(r)

            print(f"synthesis takes {end - start}")

    CloseDatabase()


if __name__ == '__main__':
    # main_demo_mas()

    main()
