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
    """
    Query 1:
    Give me all the moroccan restaurants in Texas
    """
    query_identifier = "Yelp 1"
    sketches = []
    literal_top_sketch = "select:select(restaurant), where:location(Texas), where:kind(Moroccan)"
    utterance = "Give me all the moroccan restaurants in Texas"
    solution = """
    SELECT name FROM business 
    JOIN category ON (business.business_id = category.business_id) 
    WHERE category.category_name = 'Moroccan' AND state = 'Texas';
    """
    print(f"{query_identifier} Utterance: {utterance}")
    print(f"{query_identifier} Golden Solution: {solution}")
    
    # Version 1: [Sketch works!]
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

    # Version 2: [Sketch works!]
    # Modified sketch hint columns
    p = Projection(
        Selection(
            Table(hint=Hint(["business"])),
            Predicate(operators.and_, 
                Predicate(operators.eq, Column(hint=Hint("Place")), Value("Texas") ),
                Predicate(operators.eq, Column(hint=Hint("Kind")), Value("Moroccan"))
            )
        ),
        AbstractColumns(
            Column(hint=Hint(["name"]))
        )
    )
    sketches.append(p)

    return sketches


def yelp_q2():
    query_identifier = "Yelp 2"
    sketches = []
    utterance = "List all the Italian restaurants in Los Angeles"
    literal_top_sketch = "select:select(where:kind(italian) restaurant), where:location(Los Angeles)"
    solution = """
    SELECT name FROM business 
    JOIN category ON (business.business_id = category.business_id) 
    WHERE category.category_name = 'Italian' AND business.state = 'Los Angeles';
    """
    print(f"{query_identifier} Utterance: {utterance}")
    print(f"{query_identifier} Golden Solution: {solution}")

    p = Projection(
        Selection(
            Table(hint=Hint(["business"])),
            Predicate(operators.and_, 
                Predicate(operators.eq, Column(hint=Hint("state")), Value("Los Angeles") ),
                Predicate(operators.eq, Column(hint=Hint("category_name")), Value("Italian"))
            )
        ),
        AbstractColumns(
            Column(hint=Hint(["name"]))
        )
    )
    sketches.append(p)
    return sketches

def yelp_q3():
    query_identifier = "Yelp 3"
    sketches = []
    literal_top_sketch = "agg:count(preschool), where:location(Madison)"
    utterance = "Find the number of preschools in Madison"
    solution = """
    SELECT count(preschool) FROM business 
    JOIN category ON (business.business_id = category.business_id) 
    WHERE category.category_name = 'Moroccan';
    """
    Comments = """
    - Fuzzy match: The "preschool" is tokenized by frontend such that it does not exactly match the entry "Preschools" in the table.
    - Entity misplaced: Preschool is a category instead of a entry. 
    - Madison is a city, but there are many columns that contains geographic information (state, city, address, etc). 
    """

    print(f"{query_identifier} Utterance: {utterance}")
    print(f"{query_identifier} Golden Solution: {solution}")

    # [Sketch Failed...] 
    # The preschool hint is misplaced into the count() operator.
    # p = Projection(
    #     Selection(
    #         Table(hint=Hint(["business"])),
    #         Predicate(operators.eq, Column(hint=Hint("city")), Value("Madison"))
    #     ),
    #     AbstractColumns(
    #         Aggregation(operators.count_, Column(hint=Hint("preschool")))
    #     )
    # )
    # sketches.append(p)

    p = Projection(
        Selection(
            Table(hint=Hint(["business"])),
            Predicate(operators.and_, 
                Predicate(operators.eq, Column(hint=Hint("city")), Value("Madison")),
                Predicate(operators.eq, Column(hint=Hint("category_name")), Value("Preschools")),
            )
        ),
        AbstractColumns(
            # Aggregation(operators.count_, Column(hint=Hint("preschool")))
            Aggregation(operators.count_, Column(hint=Hint("name")))
        )
    )
    sketches.append(p)
    return sketches



def yelp_q4():
    query_identifier = "Yelp 4"
    sketches = []
    literal_top_sketch = "select:select(restaurant), where:binary(rate, >, 3.5)"
    utterance = "List all the restaurants rated more than 3.5"
    solution = """
    SELECT business.name FROM business 
    JOIN category ON (business.business_id = review.business_id)
    WHERE review.rating > 3.5;
    """
    Comments = """
    - Fuzzy match `rate`: the original column name is `rating`.
    """

    print(f"{query_identifier} Utterance: {utterance}")
    print(f"{query_identifier} Golden Solution: {solution}")

    
    p = Projection(
        Selection(
            Table(hint=Hint(["business"])),
            Predicate(operators.and_, 
                Predicate(operators.gt, Column(hint=Hint("rate")), Value(3.5)),
            )
        ),
        AbstractColumns(
            # Column(hint=Hint(["restaurant"]))
            Column(hint=Hint(["name"]))
        )
    )
    sketches.append(p)
    return sketches





def main():
    db_path = "yelp.db"

    fk_pk_list = [        
        # (primary table name, primary column name, foreign table name, foreign column name)    
        ("business", "business_id", "category", "business_id"),
        ("business", "business_id", "checkin", "business_id"),
        ("business", "business_id", "neighborhood", "business_id"),
        ("business", "business_id", "review", "business_id"),
        ("business", "business_id", "tip", "business_id"),

        ("user", "user_id", "tip", "user_id"),
        ("user", "user_id", "review", "user_id"),
    ] 
    LoadDatabase(db_path, fk_pk_list=fk_pk_list)

    # queries = [yelp_q1]
    # queries = [yelp_q2]
    queries = [yelp_q3]
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
