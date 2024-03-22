import inspect

def curry(func, len_of_params=None):
    assert len_of_params is None or len_of_params >= 0, "func的参数个数不能少于0个"
    length = len_of_params if len_of_params else len(inspect.signature(func).parameters)
    def helper(params, left):
        if left == 0:
            return func(*params)
        return lambda a_para : helper(params + (a_para,), left - 1)
    return helper((), length)

