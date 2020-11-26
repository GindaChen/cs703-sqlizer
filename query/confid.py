# In the specific case of the database query synthesis problem, we make use of the following high-level insights to determine the confidence score of each type inhabitant:
# - Names of schema elements: Since our query sketches contain natural language hints for each hole, we can utilize table and column names in the database schema to assign confidence scores.
# - Foreign and primary keys: Since foreign keys provide links between data in two different database tables, join operations that involve foreign keys have a higher chance of being the intended term.
# - Database contents: Our approach also uses the contents of the database when assigning scores to queries. For instance, a candidate term sigma_phi(T) is relatively unlikely to occur in the target query if there are no entries in relation T satisfying predicate phi

from query.base import Hint
from database.table import DatabaseColumn, getDatabase
import query.param as param

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


# sim in Fig. 6
class HintConfid(BaseConfid):
    def __init__(self, hint: Hint, name: str):
        super().__init__()
        from query.word_sim import ws_model
        self.score = max(ws_model.similarity(name, h) for h in hint)


class JoinConfid(BaseConfid):
    def __init__(self, lhs_col: DatabaseColumn, rhs_col: DatabaseColumn):
        super().__init__()
        db = getDatabase()
        if db.isForeign(lhs_col, rhs_col):
            self.score = 1 - param.eps_join
        else:
            self.score = param.eps_join


class PredConfid(BaseConfid):
    def __init__(self, pred_expr: 'Predicate', c_sketch_compl: 'BaseSketchCompl', e_sketch_compl: 'BaseSketchCompl'):
        super().__init__()
        db = getDatabase()
        if db.evalPred(pred_expr, c_sketch_compl, e_sketch_compl):
            self.score = 1 - param.eps_pred
        else:
            self.score = param.eps_pred


class CastConfid(BaseConfid):
    def __init__(self, val, src_type, dst_type):
        super().__init__()
        # TODO:
        self.score = 0
        pass
