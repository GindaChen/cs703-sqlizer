from query.base import BaseExpr, BaseOperator


class QueryExpr(BaseExpr):

    def __init__(
            self,
            from_=None,
            select=None, where=None, join=None,
            group_by=None, having=None,
            # order_by=None, offset=None, limit=None
    ):
        # SQL Query starts with the `from` clause
        self.from_ = from_ or []

        # Then the select, where, join clause will scope the query schema
        # Notice: In most academic setting,
        #     - select = projection / aggregation, depending on the type of
        #                objects in the select array.
        #     - where  = selection
        self.select = select or []
        self.where = where or []
        self.join = join or []

        # Then some of the the additional constraints if aggregation is
        # contained in the select clause.
        self.group_by = group_by or []
        self.having = having or []

        # Finally, some additional inforamtion we don't care about just now.
        # self.order_by = order_by or []
        # self.offset = offset
        # self.limit = limit


class ColExpr(BaseExpr):
    def __init__(self, operator: BaseOperator, *args, **kwargs):
        self.operator = operator
        self.args = args or []
        self.kwargs = kwargs


class JoinExpr(BaseExpr):
    def __init__(self, left, right, join_type=None, predicates=None):
        self.left = left
        self.right = right
        self.join_type = join_type
        self.predicates = predicates or []
