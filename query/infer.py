# Inference rules implementation
# Fig 7 and Fig 8

from query.confid import BaseConfid
from query.type import Type


class TypeCheck():
    # if constructed from type_set, type_set must be of form: {DatabaseColumn,}
    # if constructed from col_type, col_type must be of Type
    def __init__(self, type_set: set=None, col_type: Type=None):
        if type_set is not None == col_type is None:
            raise ValueError("type_set and col_type cannot be both None or not None")
        if col_type is not None and not isinstance(col_type, Type):
            raise TypeError(f"Invalid type of col_type: {type(col_type)}")
        self.type_set = type_set
        self.col_type = col_type

    @property
    def isTypeSet(self):
        return self.type_set is not None

    # construct a new TypeCheck with only given type exists
    def typeFilter(self, filter_type: Type):
        assert self.type_set is not None
        new_type_set = set()
        for c in self.type_set:
            if c.type_ == filter_type:
                new_type_set.add(c)
        return TypeCheck(type_set=new_type_set)


class BaseSketchCompl():
    def __init__(self):
        self.confid = BaseConfid(0.)

    def __lt__(self, other):
        return self.confid < other.confid


class SingleSketchCompl(BaseSketchCompl):
    # compl is a completion map Hint to DatabaseTable/DatabaseColumn to fill in
    def __init__(self, compl: dict, confid: BaseConfid, type_check: TypeCheck):
        super().__init__()
        self.compl = compl
        self.confid = confid
        self.type_check = type_check


class ComposeSketchCompl(BaseSketchCompl):
    def __init__(self, from_list, more_confid=None):
        super().__init__()
        self.sub_compl = from_list
        self.more_confid = more_confid
        # we must preserve hierarchy for fault localization, but it is okay to flatten confidence and type_check
        confids = [sc.confid for sc in from_list]
        if more_confid is not None:
            confids.append(more_confid)
        self.confid = BaseConfid.compose(confids)
        type_set = set()
        for sc in from_list:
            type_set.update(sc.type_check.type_set)
        self.type_check = TypeCheck(type_set)


# The inference rules produce a list of completion sorted by confidence
