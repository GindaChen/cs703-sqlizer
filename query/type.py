class Type():
    pass


class BooleanType(Type):
    pass


class NumericType(Type):
    pass


class StringType(Type):
    pass


boolean = BooleanType()
numeric = NumericType()
string = StringType()

types = [boolean, numeric, string]


def equal_types(n=2):
    """Return the list of possible types."""
    return [[t] * n for t in types]
