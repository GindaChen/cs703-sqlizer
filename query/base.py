from query.type import boolean, equal_types


class BaseExpr():
    pass


class BaseOperator():
    pass


class Operator(BaseOperator):
    def __init__(self, name, arity, input_type, output_type):
        self.name = name
        self.arity = arity
        self.input_type = input_type
        self.output_type = output_type

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
