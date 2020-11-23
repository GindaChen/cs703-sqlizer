from query.base import Operator, AggregateFunc
from query.type import equal_types

# ------------------------------------
#       Boolean Operators
# ------------------------------------
eq = Operator.BinaryBoolean('=')
lt = Operator.BinaryBoolean('<')
gt = Operator.BinaryBoolean('>')
le = Operator.BinaryBoolean('<=')
ge = Operator.BinaryBoolean('>=')

# ------------------------------------
#       Logical Boolean Operators
# ------------------------------------
neg = Operator.UnaryBoolean('!')
and_ = Operator.BinaryBoolean('AND')
or_ = Operator.BinaryBoolean('OR')

# Note: != is just !( x = y ). Think about if we want to keep it.
# ne = Operator.BinaryBoolean('!=')

# Note: This iteration we don't care about numeric exprs
# add = Operator.BinaryNumeric('+')
# minus = Operator.BinaryNumeric('-')
# multiply = Operator.BinaryNumeric('*')
# divide = Operator.BinaryNumeric('/')

# ------------------------------------
#       Aggregate Operators
# ------------------------------------
max_ = AggregateFunc.NumericAggregateFunc('max')
min_ = AggregateFunc.NumericAggregateFunc('min')
count_ = AggregateFunc.NumericAggregateFunc('count', input_type=equal_types(1))
sum_ = AggregateFunc.NumericAggregateFunc('sum')
avg_ = AggregateFunc.NumericAggregateFunc('avg')

all_aggregates = [max_, min_, count_, sum_, avg_]