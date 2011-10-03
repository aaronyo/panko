def seqify(value):
    if hasattr(value, '__iter__'):
        return value
    else:
        return [value]