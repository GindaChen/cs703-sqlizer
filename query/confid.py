# In the specific case of the database query synthesis problem, we make use of the following high-level insights to determine the confidence score of each type inhabitant:
# - Names of schema elements: Since our query sketches contain natural language hints for each hole, we can utilize table and column names in the database schema to assign confidence scores.
# - Foreign and primary keys: Since foreign keys provide links between data in two different database tables, join operations that involve foreign keys have a higher chance of being the intended term.
# - Database contents: Our approach also uses the contents of the database when assigning scores to queries. For instance, a candidate term sigma_phi(T) is relatively unlikely to occur in the target query if there are no entries in relation T satisfying predicate phi

from query.word_sim import ws_model
from query.base import Hint
from database.table import DatabaseColumn, getDatabase
from query.type import Type, boolean, numeric, string
import query.params as params


class BaseConfid():
    def __init__(self, score: float=0):
        self.score = score

    @classmethod # compose a list of confidence
    def compose(cls, confids):
        p = 1
        for c in confids:
            p *= c.score
        return BaseConfid(score=p ** (1 / len(confids)))

    def __mul__(self, other):
        return BaseConfid.compose([self, other])

    # used by sort()
    def __lt__(self, other):
        return self.score < other.score

    def __repr__(self):
        return f'confid={self.score:.4f}'


# sim in Fig. 6
class HintConfid(BaseConfid):
    def __init__(self, hint: Hint, name: str):
        super().__init__()
        # we split the name (e.g., `Conference.cid`) into two parts and take the average among parts
        # for multiple hints, we take the maximum value
        parts = name.lower().split(".")
        self.score = max(
            (
                sum(ws_model.similarity(p, h) for p in parts) / len(parts)
                for h in hint
            ),
            default=0.5
        )


class JoinConfid(BaseConfid):
    def __init__(self, lhs_col: DatabaseColumn, rhs_col: DatabaseColumn):
        super().__init__()
        if (lhs_col.foreign_of is rhs_col) or (rhs_col.foreign_of is lhs_col):
            self.score = 1 - params.eps_join
        else:
            self.score = params.eps_join


class PredConfid(BaseConfid):
    def __init__(self, pred_expr: 'Predicate', c_sketch_compl: 'BaseSketchCompl', e_sketch_compl: 'BaseSketchCompl'):
        super().__init__()
        db = getDatabase()
        if db.evalPred(pred_expr, c_sketch_compl, e_sketch_compl):
            self.score = 1 - params.eps_pred
        else:
            self.score = params.eps_pred


class CastConfid(BaseConfid):
    def __init__(self, val, src_type: Type, dst_type: Type):
        super().__init__()
        if src_type == dst_type:
            self.score = 1 # cast to the same type should always be okay
            return
        if src_type == boolean or dst_type == boolean:
            self.score = params.eps_cast # it doesn't really make sense to case boolean
            return
        if src_type == numeric and dst_type == string:
            self.score = params.fine_cast
            return
        if src_type == string and dst_type == numeric:
            self.score = params.fine_cast
            try:
                int(val)
            except ValueError: # fail to cast string to int
                self.score = params.eps_cast
            return
        raise TypeError(f"Unknown type: src_type: {type(src_type)}, dst_type: {type(dst_type)}")
