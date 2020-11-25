# Inference rules implementation
# Fig 7 and Fig 8

from query.confid import BaseConfid
from query.type import Type


class TypeCheck():
    # if constructed from type_set, type_set must be of form: {DatabaseColumn,}
    # if constructed from col_type, col_type must be of Type
    def __init__(self, type_set: set=None, col_type: Type=None):
        if (type_set is None) == (col_type is None):
            raise ValueError("type_set and col_type cannot be both None or not None")
        if col_type is not None and not isinstance(col_type, Type):
            raise TypeError(f"Invalid type of col_type: {type(col_type)}")
        self.type_set = type_set
        self.col_type = col_type

    @property
    def isTypeSet(self):
        return self.type_set is not None

    # construct a new TypeCheck with only given type exists
    # filter_type could be a Type object, or a list of Type
    def typeFilter(self, filter_type):
        assert self.type_set is not None
        if isinstance(filter_type, Type):
            filter_type = [filter_type]
        new_type_set = set()
        for c in self.type_set:
            if c.type_ in filter_type:
                new_type_set.add(c)
        return TypeCheck(type_set=new_type_set)
    
    # construct a new TypeCheck from union a TypeCheck list
    @classmethod
    def typeUnion(cls, from_list):
        new_type_set = set()
        for t in from_list:
            new_type_set = new_type_set.union(t.type_set)
        return TypeCheck(type_set=new_type_set)


# SketchCompl should work like a dict, which map Hint to string
class BaseSketchCompl():
    def __init__(self):
        self.confid = None

    def __lt__(self, other):
        return self.confid < other.confid


class SingleSketchCompl(BaseSketchCompl):
    # compl is a completion map Hint to DatabaseTable/DatabaseColumn to fill in
    def __init__(self, compl: dict, confid: BaseConfid, type_check: TypeCheck):
        super().__init__()
        self.compl = compl
        self.confid = confid
        self.type_check = type_check
    
    def __getitem__(self, item: BaseConfid):
        return self.compl.get(item)


class ComposeSketchCompl(BaseSketchCompl):
    # if type_check is not specified, the union of from_list's type will be used
    def __init__(self, from_list, type_check: TypeCheck=None, more_confid=None):
        super().__init__()
        self.sub_compl = from_list
        self.more_confid = more_confid
        # we must preserve hierarchy for fault localization, but it is okay to flatten confidence and type_check
        confids = [sc.confid for sc in from_list]
        if more_confid is not None:
            confids.append(more_confid)
        self.confid = BaseConfid.compose(confids)
        if type_check is not None:
            self.type_check = type_check
        else:
            type_set = set()
            for sc in from_list:
                type_set = type_set.union(sc.type_check.type_set)
            self.type_check = TypeCheck(type_set=type_set)

    # compose a TypeCheck from a list of SketchCompl
    @classmethod
    def typeCompose(cls, from_list):
        new_type_set = set()
        for sc in from_list:
            new_type_set = new_type_set.union(sc.type_check.type_set)
        return TypeCheck(type_set=new_type_set)

    def getSubCompl(self, idx: int):
        return self.sub_compl[idx]


# this is only used for unparse to indicate a None sketch completion
# when passing this as the skecth completion for unparse, print the hole instead of what is filled
class UnparseDefaultSketchCompl(ComposeSketchCompl):
    def __init__(self):
        pass

    # always return self
    def getSubCompl(self, idx: int):
        return self


# Do not export UnparseDefaultSketchCompl
# instead, only export NoneSketchCompl
NoneSketchCompl = UnparseDefaultSketchCompl()

# The inference rules produce a list of completion sorted by confidence
