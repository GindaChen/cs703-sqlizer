"""
Extended Relational Algebra
    Table   :=  Proj(Columns, Table)
            |   Select(Predicate, Table)
            |   Join(Table_1, Table_2, c)
            |   t
    Columns := Columns_1 + Columns_2
            | [c]              # List of column
            | agg(c, Columns)
            | group(agg(c1, Columns), c2) # must separated from agg due to sketch requirement
    Predicate := lop(Predicate, Predicate)
            | neg(Predicate)
            | op(c, Entity)  # Consider only binary operators
    Entity  := Table | c | v
    t := <table name>
    c := <column name>
    v := <value>
    agg := <aggregate functions>
    lop := and | or
    op  := < | <= | > | >= | =
"""
from typing import List

import query.operators as ops
from query.type import boolean, numeric, string
from database.table import DatabaseColumn, DatabaseTable
from query.base import BaseExpr, AggregateFunc, Operator, Hint
from query.infer import BaseSketchCompl, SingleSketchCompl, ComposeSketchCompl, NoneSketchCompl, TypeCheck
from query.confid import BaseConfid, HintConfid, JoinConfid, PredConfid, CastConfid
from database.table import getDatabase

"""
Inherence Structure
BaseExpr
    - Entity (E)
        - AbstractTable (T)
            - Projection
            - Selection
            - Join
            - Table (t)
        - Value (v)
        - Column (c)
    - AbstractColumns (L)
    - GroupAgg (g)
    - Aggregation (f)
    - Predicate (phi)
"""


# inherited by AbstractTable, Column, Value
# this is "E"
class Entity(BaseExpr):
    def __init__(self):
        super().__init__()

    # its subclass must implement unparse()


# inherited by Projection, Selection, Join, and Table
# this is "T"
class AbstractTable(Entity):
    def __init__(self):
        super().__init__()

    def unparse(self, indent=0, sketch_compl: BaseSketchCompl=NoneSketchCompl):
        pass

    # its subclass must implement unparse()


# this is "L", but it must be a list of c, f(c), or g(f(c), c). No L itself as an element.
class AbstractColumns(BaseExpr):
    def __init__(self, c=None, lhs=None, rhs=None, from_list=None):
        super().__init__()
        # from_col_list is a syntax sugar... directly construct from a list of Column
        if from_list is not None:
            for c in from_list:
                if not isinstance(c, Column) and not isinstance(c, GroupAgg) and not isinstance(c, Aggregation):
                    raise TypeError("Invalid Type: {}".format(str(type(c))))
            self.col_list = from_list
            return

        if (lhs is None) != (rhs is None):
            raise ValueError("lhs and rhs must both be supplied or both not")
        if lhs is None and rhs is None:
            if c is None:
                raise ValueError("All arguments cannot be all None")
            else:
                if not isinstance(c, Column) and not isinstance(c, GroupAgg) and not isinstance(c, Aggregation):
                    raise TypeError(f'Invalid Type: {str(type(c))}')
                self.col_list = [c]
        else:
            if c is not None:
                raise ValueError("All arguments cannot be all supplied")
            else:
                self.col_list = lhs.col_list + rhs.col_list

    def unparse(self, indent=0, sketch_compl: ComposeSketchCompl=NoneSketchCompl):
        return ", ".join([self.col_list[i].unparse(indent, sketch_compl.getSubCompl(i))
            for i in range(len(self.col_list))])
    
    # Note our implementation may be different from the paper
    # the paper compose two scores each time
    # but we compose them all together
    # given the weired definition of confidence composition function, these two results might not be equivalent
    def infer(self, type_check: TypeCheck=None):
        # TODO: optimization: filter duplication column
        assert type_check is not None
        sub_candi_list = self.candi_permute_helper(start=0, type_check=type_check)
        candidates = [ComposeSketchCompl(candi_list) for candi_list in sub_candi_list]
        candidates.sort(reverse=True) # sorted by confid, from high to low
        return candidates

    def candi_permute_helper(self, start, type_check: TypeCheck):
        if start == len(self.col_list) - 1:
            return [[c] for c in self.col_list[start].getCandidates(type_check)]
        return [[head] + tail
            for head in self.col_list[start].getCandidates(type_check)
            for tail in self.candi_permute_helper(start + 1, type_check)]


# this is "v"
class Value(Entity):
    def __init__(self, val):
        super().__init__()
        if isinstance(val, bool):
            self.type = boolean
        elif isinstance(val, int):
            self.type = numeric
        elif isinstance(val, str):
            self.type = string
        else:
            TypeError(f'Invalid Type: {str(type(val))}')
        self.val = val

    def unparse(self, indent=0, sketch_compl: BaseSketchCompl=NoneSketchCompl):
        if isinstance(self.val, str):
            return f'"{self.val}"'
        return str(self.val)
    
    def infer(self, type_check: TypeCheck=None):
        assert type_check is not None
        possible_types = set(c.type_ for c in type_check.type_set)
        candidates = [SingleSketchCompl({}, confid=CastConfid(self.val, self.type, t),
            type_check=TypeCheck({DatabaseColumn.valueDatabaseColumn(t)}))
            for t in possible_types]
        candidates.sort(reverse=True)
        return candidates


# this is "c", a single column name
class Column(Entity):
    def __init__(self, col_name=None, hint: Hint=None):
        super().__init__()
        self.col_name = col_name
        self.hint = hint
    
    @property
    def isHole(self):
        return self.hint is not None # if this hole has no hint, it should at least have a Hint() with empty hint
    
    def unparse(self, indent=0, sketch_compl: BaseSketchCompl=NoneSketchCompl):
        if self.isHole:
            if sketch_compl == NoneSketchCompl:
                return f'?{self.hint}'
            else:
                assert isinstance(sketch_compl, SingleSketchCompl)
                return sketch_compl[self.hint].name
        return self.col_name

    def infer(self, type_check: TypeCheck=None):
        assert self.isHole
        assert type_check is not None
        candidates = [SingleSketchCompl({self.hint: c}, HintConfid(self.hint, c.name), type_check=TypeCheck({c}))
            for c in type_check.type_set]
        candidates.sort(reverse=True)
        return candidates


# this is "t", a single table name
class Table(AbstractTable):
    def __init__(self, table_name=None, hint: Hint=None):
        super().__init__()
        self.table_name = table_name
        self.hint = hint

    @property
    def isHole(self):
        return self.hint is not None # if this hole has no hint, it should at least have a Hint() with empty hint
    
    def unparse(self, indent=0, sketch_compl: BaseSketchCompl=NoneSketchCompl):
        if self.isHole:
            if sketch_compl == NoneSketchCompl:
                return f'??{self.hint}'
            else:
                return sketch_compl[self.hint].name
        return self.table_name

    def infer(self, type_check: TypeCheck=None):
        assert self.isHole
        assert type_check is None  # Table's infer must not have any type check constraints
        candidates = []
        db = getDatabase()
        for table_name, table in db.getAllTables():
            table_type_check = TypeCheck(type_set=set(table.getAllColumnObjs())) # export type check info
            candidate = SingleSketchCompl({self.hint: table}, HintConfid(self.hint, table_name), table_type_check)
            candidates.append(candidate)
        candidates.sort(reverse=True) # sorted by confid, from high to low
        return candidates


class GroupAgg(BaseExpr):
    def __init__(self, agg, by_col: Column):
        super().__init__()
        self.agg = agg
        self.by_col = by_col

    def unparse(self, indent=0, sketch_compl: ComposeSketchCompl=NoneSketchCompl):
        # only print agg here and leave by_col handled by Projection
        return self.agg.unparse(indent, sketch_compl.getSubCompl(0))

    def infer(self, type_check: TypeCheck=None):
        assert type_check is not None
        candidates = [ComposeSketchCompl([c1, c2])
            for c1 in self.agg.getCandidates(type_check)
            for c2 in self.by_col.getCandidates(type_check)]
        candidates.sort(reverse=True) # sorted by confid, from high to low
        return candidates


class Aggregation(BaseExpr):
    def __init__(self, func: AggregateFunc, col: Column):
        super().__init__()
        self.func = func
        self.col = col

    def unparse(self, indent=0, sketch_compl: ComposeSketchCompl=NoneSketchCompl):
        return f'{self.func}({self.col.unparse(indent, sketch_compl.getSubCompl(0))})'
    
    def infer(self, type_check: TypeCheck=None):
        assert type_check is not None
        candidates = []
        input_type = self.func.input_type
        for c1 in self.col.getCandidates(type_check.typeFilter(input_type)):
            tmp_db_col = DatabaseColumn.aggDatabaseColumn(agg_expr=self)
            candidates.append(ComposeSketchCompl([c1], type_check=TypeCheck({tmp_db_col})))
        candidates.sort(reverse=True) # sorted by confid, from high to low
        return candidates


class Predicate(BaseExpr):
    def __init__(self, func, *args):
        super().__init__()
        self.func: Operator = func
        self.args = args
        assert self.func.arity == len(self.args)

    def unparse(self, indent=0, sketch_compl: ComposeSketchCompl=NoneSketchCompl):
        func = self.func.name
        arity = self.func.arity
        if arity == 1:
            v = self.args[0].unparse(indent, sketch_compl.getSubCompl(0))
            return f'{func}({v})'
        elif arity == 2:
            lhs = self.args[0].unparse(indent, sketch_compl.getSubCompl(0))
            rhs = self.args[1].unparse(indent, sketch_compl.getSubCompl(1))
            return f'({lhs} {func} {rhs})'
        else:
            raise ValueError("Incorrect arity")
    
    def infer(self, type_check: TypeCheck=None):
        assert type_check is not None
        candidates = []
        # handle three cases: Pred, PredNeg, PredLop
        if self.func == ops.neg: # handle PredNeg
            candidates = [ComposeSketchCompl([c1], type_check=TypeCheck(col_type=boolean))
                for c1 in self.args[0].getCandidates(type_check)]
        elif self.func == ops.and_ or self.func == ops.or_:
            candidates = [ComposeSketchCompl([c1, c2], type_check=TypeCheck(col_type=boolean))
                for c1 in self.args[0].getCandidates(type_check)
                for c2 in self.args[1].getCandidates(type_check)]
        else: # handle eq, lt, gt, le, ge
            lhs_c, rhs_e = self.args
            for c1 in lhs_c.getCandidates(type_check):
                lhs_c_type = next(iter(c1.type_check.type_set)).type_
                # c2 must have same type as c1; apply type filter
                for c2 in rhs_e.getCandidates(type_check.typeFilter(lhs_c_type)):
                    candidates.append(ComposeSketchCompl([c1, c2], type_check=TypeCheck(col_type=boolean),
                        more_confid=PredConfid(self, c1, c2)))
        candidates.sort(reverse=True)
        return candidates


class Projection(AbstractTable):
    def __init__(self, abs_table: AbstractTable, abs_cols: AbstractColumns):
        super().__init__()
        self.abs_table = abs_table
        self.abs_cols = abs_cols

    def unparse(self, indent=0, sketch_compl: ComposeSketchCompl=NoneSketchCompl):
        if isinstance(self.abs_table, Projection): # nested SELECT
            abs_table_unparse_result = f'({self.abs_table.unparse(indent + 1, sketch_compl.getSubCompl(0))})'
        else:
            abs_table_unparse_result = self.abs_table.unparse(indent, sketch_compl.getSubCompl(0))
        proj_body = f'SELECT {self.abs_cols.unparse(indent, sketch_compl.getSubCompl(1))}\n{mkIndent(indent)}'\
                    f'FROM {abs_table_unparse_result}'
        group_by_cols = []
        for i in range(len(self.abs_cols.col_list)):
            c = self.abs_cols.col_list[i]
            if isinstance(c, GroupAgg):
                group_by_cols.append(c.by_col.unparse(indent, sketch_compl.getSubCompl(1).getSubCompl(i).getSubCompl(1)))
        group_by_cols = set(group_by_cols) # deduplicate
        if len(group_by_cols) > 0:
            proj_body += f'\n{mkIndent(indent)}GROUP BY '
            proj_body += ', '.join(group_by_cols)
        return proj_body
    
    def infer(self, type_check: TypeCheck=None):
        assert type_check is None # projection must not have any type check constraints
        candidates = []
        for c1 in self.abs_table.getCandidates():
            for c2 in self.abs_cols.getCandidates(c1.type_check):
                candidates.append(ComposeSketchCompl([c1, c2], type_check=c2.type_check))
        candidates.sort(reverse=True) # sorted by confid.
        return candidates


class Selection(AbstractTable):
    def __init__(self, abs_table: AbstractTable, pred: Predicate):
        super().__init__()
        self.abs_table = abs_table
        self.pred = pred

    def unparse(self, indent=0, sketch_compl: ComposeSketchCompl=NoneSketchCompl):
        if isinstance(self.abs_table, Projection): # nested SELECT
            abs_table_unparse_result = f'({self.abs_table.unparse(indent + 1, sketch_compl.getSubCompl(0))})'
        else:
            abs_table_unparse_result = self.abs_table.unparse(indent, sketch_compl.getSubCompl(0))
        return f'{abs_table_unparse_result}\n'\
            f'{mkIndent(indent)}WHERE {self.pred.unparse(indent + 1, sketch_compl.getSubCompl(1))}'

    def infer(self, type_check: TypeCheck=None):
        assert type_check is None # selection must not have any type check constraints
        candidates = []
        for c1 in self.abs_table.getCandidates():
            for c2 in self.pred.getCandidates(c1.type_check):
                candidates.append(ComposeSketchCompl([c1, c2], type_check=c1.type_check))
        candidates.sort(reverse=True) # sorted by confid.
        return candidates


class Join(AbstractTable):
    def __init__(self, lhs_abs_table: AbstractTable, rhs_abs_table: AbstractTable, lhs_col: Column, rhs_col: Column):
        super().__init__()
        self.lhs_abs_table = lhs_abs_table
        self.rhs_abs_table = rhs_abs_table
        self.lhs_col = lhs_col
        self.rhs_col = rhs_col
    
    def unparse(self, indent=0, sketch_compl: ComposeSketchCompl=NoneSketchCompl):
        if isinstance(self.lhs_abs_table, Projection): # nested SELECT
            lhs_abs_table_unparse_result = f'({self.lhs_abs_table.unparse(indent + 1, sketch_compl.getSubCompl(0))})'
        else:
            lhs_abs_table_unparse_result = self.lhs_abs_table.unparse(indent, sketch_compl.getSubCompl(0))
        if isinstance(self.rhs_abs_table, Projection): # nested SELECT
            rhs_abs_table_unparse_result = f'({self.rhs_abs_table.unparse(indent + 1, sketch_compl.getSubCompl(1))})'
        else:
            rhs_abs_table_unparse_result = self.rhs_abs_table.unparse(indent, sketch_compl.getSubCompl(1))
        return f'{lhs_abs_table_unparse_result} JOIN '\
            f'{rhs_abs_table_unparse_result} ON '\
            f'{self.lhs_col.unparse(indent, sketch_compl.getSubCompl(2))} = '\
            f'{self.rhs_col.unparse(indent, sketch_compl.getSubCompl(3))}'

    def infer(self, type_check: TypeCheck=None):
        assert type_check is None # join must not have any type check constraints
        candidates = []
        for c1 in self.lhs_abs_table.getCandidates():
            for c2 in self.rhs_abs_table.getCandidates():
                # TODO: optimization: c1 and c2 are not referring to the same table
                for c3 in self.lhs_col.getCandidates(c1.type_check):
                    join_col_lhs = next(iter(c3.type_check.type_set))
                    filter_type = join_col_lhs.type_
                    # c4 must be columns in c2 and same type as c3
                    for c4 in self.rhs_col.getCandidates(c2.type_check.typeFilter(filter_type)):
                        join_col_rhs = next(iter(c4.type_check.type_set))
                        candidates.append(ComposeSketchCompl([c1, c2, c3, c4],
                            type_check=ComposeSketchCompl.typeCompose([c1, c2]),
                            more_confid=JoinConfid(join_col_lhs, join_col_rhs)))
        candidates.sort(reverse=True) # sorted by confid.
        return candidates


# unparse helper
def mkIndent(n):
    return "".join(['\t' for _ in range(n)])
