def seqify(value):
    if hasattr(value, '__iter__'):
        return value
    else:
        return [value]
        
def join_items(seq, delim):
    if hasattr(seq, '__iter__') and all(isinstance(val, str) or isinstance(val, unicode) for val in seq):
        return [delim.join(seq)]
    return seq