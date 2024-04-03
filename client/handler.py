def forever():
    n = 0
    while 1:
        n += 1
        yield n

class Handler:
    def multi_apply(func, times=forever()):
        for i in times:
            try:
                result = func()
                # 避免func返回None
                return result if result else 'sucess'
            except Exception as err:
                func_signatrue = str(func).split()[1]
        print(f'函数{func_signatrue}调用失败, 完全退出')
        return False

    def apply(func, error_message=''):
        return Handler.multi_apply(func, range(1, 2))

