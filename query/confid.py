# In the specific case of the database query synthesis problem, we make use of the following high-level insights to determine the confidence score of each type inhabitant:
# - Names of schema elements: Since our query sketches contain natural language hints for each hole, we can utilize table and column names in the database schema to assign confidence scores.
# - Foreign and primary keys: Since foreign keys provide links between data in two different database tables, join operations that involve foreign keys have a higher chance of being the intended term.
# - Database contents: Our approach also uses the contents of the database when assigning scores to queries. For instance, a candidate term sigma_phi(T) is relatively unlikely to occur in the target query if there are no entries in relation T satisfying predicate phi

from query.base import Hint
from query.expr import Entity, AbstractTable, AbstractColumns, Value, Column, Table, \
    GroupAgg, Aggregation, Predicate, Projection, Selection, Join

class BaseConfid():
    def __init__(self):
        pass
    
    @classmethod # compose a list of confidence
    def compose(*confids):
        p = 1
        for c in confids:
            p *= c.score
        return p ** (1 / len(confids))

    def __mul__(self, other):
        return BaseConfid.compose(self, other)


# sim in Fig. 6
class HintConfid(BaseConfid):
    def __init__(self, hint: Hint, col: Column):
        super().__init__()
        self.score = 0 # to set
        # TODO: Word2Vec...
        pass


class JoinConfid(BaseConfid):
    def __init__(self, lhs_col: Column, rhs_col: Column):
        super().__init__()
        self.score = 0 # to set
        # TODO: foregin key...
        pass


class PredConfid(BaseConfid):
    def __init__(self, col: Column, val: Value):
        super().__init__()
        self.score = 0 # to set
        # TODO: db content...
        pass
