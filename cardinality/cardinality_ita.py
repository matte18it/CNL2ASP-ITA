def cardinality(value):
    return value
def exactly(value):
    return f"= {value}"
def at_most(value):
    return f"<= {value}"
def at_least(value):
    return f">= {value}"
def between(number_1, number_2):
    return [f">= {number_1}", f"<= {number_2}"]