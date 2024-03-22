from util.logger import mailbot_log as log

def forever():
    n = 0
    while 1:
        n += 1
        yield n

class Handler:
    def multi_apply(func, times=forever(), error_message='', sucess_message=''):
        for i in times:
            try:
                result = func()
                log.logger.info(f"调用成功，总计尝试{i}次")
                # 避免func返回None
                return result if result else 'sucess'
            except Exception:
                func_signatrue = str(func).split()[1]
                log.logger.error(f"函数{func_signatrue}第{i}次调用失败！")
                log.logger.exception(Exception)
        log.logger.exception(f'函数{func_signatrue}调用失败, 完全退出')
        return False

