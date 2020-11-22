import typing

from query.type import boolean, equal_types, numeric

if typing.TYPE_CHECKING:
    from query.expr import Aggregation

class BaseExpr():
    def __init__(self):
        self.all_candidates = None
        pass

    def __str__(self):
        return self.unparse()

    # all subclasses must inplement self.infer()
    # if we want to implement some filter (e.g. only pick the first k candidates)
    # we could implement it here
    def getCandidates(self, type_check: 'TypeCheck'=None):
        if type_check is None: # then enumerate!
            if self.all_candidates is None:
                self.all_candidates = self.infer() # construct all candidates
            return self.all_candidates
        # else, use type info
        return self.infer(type_check)

class Hint():
    def __init__(self, hint=None):
        self.hint = hint or []
        if isinstance(self.hint, str): # sugar: construct from a single string
            self.hint = [self.hint]

    def __str__(self):
        if not self.hint:
            return ''
        hint_strs = ', '.join([str(i) for i in self.hint])
        return '[' + hint_strs + ']'


class BaseOperator():
    pass


class Operator(BaseOperator):
    def __init__(self, name, arity, input_type, output_type):
        self.name = name
        self.arity = arity
        self.input_type = input_type
        self.output_type = output_type

    def __call__(self, *args, **kwargs):
        from query.expr import Predicate
        if len(args) != self.arity:
            raise ValueError(
                f'Expect operator {self.name} to have arity={self.arity}, '
                f'got {len(args)}.')
        return Predicate(self, *args)

    @classmethod
    def BinaryBoolean(cls, name):
        arity = 2
        return Operator(
            name=name,
            arity=arity,
            input_type=equal_types(arity),
            output_type=boolean,
        )

    @classmethod
    def UnaryBoolean(cls, name):
        arity = 1
        return Operator(
            name=name,
            arity=arity,
            input_type=equal_types(arity),
            output_type=boolean,
        )

    @classmethod
    def BinaryNumeric(cls, name):
        arity = 2
        return Operator(
            name,
            arity=arity,
            input_type=equal_types(arity),
            output_type=boolean)


class Function(BaseOperator):
    pass


class AggregateFunc(Function):
    def __init__(self, name, input_type, output_type):
        self.name = name
        self.input_type = input_type
        self.output_type = output_type

    def __call__(self, col, *group_by) -> 'Aggregation':
        from query.expr import Aggregation
        return Aggregation(func=self, col=col, group_by=group_by)

    @classmethod
    def NumericAggregateFunc(cls, name):
        return AggregateFunc(name, input_type=equal_types(1),
                             output_type=numeric)

    def __str__(self):
        return self.name
