from query.base import AggregateFunc

max_ = AggregateFunc.NumericAggregateFunc('max')
min_ = AggregateFunc.NumericAggregateFunc('min')
count_ = AggregateFunc.NumericAggregateFunc('count')
sum_ = AggregateFunc.NumericAggregateFunc('sum')
avg_ = AggregateFunc.NumericAggregateFunc('avg')