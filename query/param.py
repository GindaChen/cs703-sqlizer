# This file defines some parameters that need tuning
# If there are more parameters to add in the future, please add them to this file

# To use these paramters:
# import query.param as param
# xxx = param.eps_join

# the confidence if the lhs and rhs columns of join clause are not primary/foreign key relationship
eps_join = 0.01

# the confidence if a predicate is always false in the given database
eps_pred = 0.01

# the confidence if a type casting is not reasonable
eps_cast = 0.01

fine_cast = 0.8
