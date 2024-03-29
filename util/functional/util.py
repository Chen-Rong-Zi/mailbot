import inspect
from functools import reduce


def curry(func, len_of_params= None):
    assert len_of_params is None or len_of_params >= 0, "func的参数个数不能少于0个"
    length = len_of_params if len_of_params else len(inspect.signature(func).parameters)
    def helper(params, left):
        if left == 0:
            return func(*params)
        return lambda a_para : helper(params + (a_para,), left - 1)
    return helper((), length)

def compose(working_list, material):
    return reduce(lambda pre, curr: curr(pre), working_list, material)

def flat(seq):
    if (not hasattr(seq, '__iter__')) or isinstance(seq, dict):
        return [seq]
    result = sum([flat(item) for item in seq], [])
    return result

def identity(x):
    return x

def not_none(x):
    return x is not None

def is_none(x):
    return x is None

