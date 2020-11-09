from query.base import Operator

eq = Operator.BinaryBoolean('=')
neg = Operator.UnaryBoolean('!')
lt = Operator.BinaryBoolean('<')
gt = Operator.BinaryBoolean('>')
le = Operator.BinaryBoolean('<=')
ge = Operator.BinaryBoolean('>=')



# Note: != is just !( x = y ). Think about if we want to keep it.
# ne = Operator.BinaryBoolean('!=')

# Note: This iteration we don't care about numeric exprs
# add = Operator.BinaryNumeric('+')
# minus = Operator.BinaryNumeric('-')
# multiply = Operator.BinaryNumeric('*')
# divide = Operator.BinaryNumeric('/')
