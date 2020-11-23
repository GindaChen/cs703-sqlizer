# In the specific case of the database query synthesis problem, we make use of the following high-level insights to determine the confidence score of each type inhabitant:
# - Names of schema elements: Since our query sketches contain natural language hints for each hole, we can utilize table and column names in the database schema to assign confidence scores.
# - Foreign and primary keys: Since foreign keys provide links between data in two different database tables, join operations that involve foreign keys have a higher chance of being the intended term.
# - Database contents: Our approach also uses the contents of the database when assigning scores to queries. For instance, a candidate term sigma_phi(T) is relatively unlikely to occur in the target query if there are no entries in relation T satisfying predicate phi

from query.base import Hint
from query.expr import Entity, AbstractTable, AbstractColumns, Value, Column, Table, \
    GroupAgg, Aggregation, Predicate, Projection, Selection, Join
from database.table import DatabaseColumn
from query.infer import BaseSketchCompl

class BaseConfid():
    def __init__(self):
        pass
    
    @classmethod # compose a list of confidence
    def compose(cls, confids):
        p = 1
        for c in confids:
            p *= c.score
        return p ** (1 / len(confids))

    def __mul__(self, other):
        return BaseConfid.compose([self, other])
    
    # used by sort()
    def __lt__(self, other):
        return self.score < other.score


# sim in Fig. 6
class HintConfid(BaseConfid):
    def __init__(self, hint: Hint, name: str):
        super().__init__()
        self.score = 0 # to set
        # TODO: Word2Vec...
        pass


class JoinConfid(BaseConfid):
    def __init__(self, lhs_col: DatabaseColumn, rhs_col: DatabaseColumn):
        super().__init__()
        self.score = 0 # to set
        # TODO: foregin key...
        # return 1 - eps,   if c 1 is a foreign key referring to c 2 (or vice versa)
        # return eps,       otherwise
        pass


class PredConfid(BaseConfid):
    def __init__(self, pred_expr: Predicate, c_sketch_compl: BaseSketchCompl, e_sketch_compl: BaseSketchCompl):
        super().__init__()
        self.score = 0 # to set
        # TODO: db content...
        # evaluye whether pred_expr with sketch_compl can be evaluted to true
        pass

class CastConfid(BaseConfid):
    def __init__(self, val, src_type, dst_type):
        super().__init__()
        # TODO: 
        self.score = 0
        pass
