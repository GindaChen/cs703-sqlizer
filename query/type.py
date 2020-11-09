class Type():
    pass


class BooleanType(Type):
    def __str__(self):
        return 'boolean'
    pass


class NumericType(Type):
    def __str__(self):
        return 'numeric'
    pass


class StringType(Type):
    def __str__(self):
        return 'string'
    pass


boolean = BooleanType()
numeric = NumericType()
string = StringType()

types = [boolean, numeric, string]


def equal_types(n=2):
    """Return the list of possible types for easy construction.
    >>> equal_types(n=1) == [[boolean], [numeric], [string]]
    >>> equal_types(n=2) == [[boolean, boolean], [numeric, numeric], [string, string]]
    """
    return [[t] * n for t in types]
