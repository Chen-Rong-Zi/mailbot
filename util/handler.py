from time        import sleep

from util.logger import fetch_log
from util.logger import mailbot_log

def forever(n):
    yield n
    yield from forever(n+1)

class Handler:
    def multi_apply(func, times=forever(1), error_message='', sucess_message='', log_file='fetch.log', sleeping_time=0):
        log = {'fetch.log' : fetch_log, 'mailbot.log' : mailbot_log}[log_file]
        for i in times:
            sleep(sleeping_time)
            try:
                result = func()
                log.logger.info(f"调用{str(func).split()[1]}成功，总计尝试{i}次, sucess_message: {sucess_message}")
                # 避免func返回None
                return result if result else 'sucess'
            except Exception as err:
                func_signatrue = str(func).split()[1]
                log.logger.error(f"函数{func_signatrue}第{i}次调用失败！错误：{err}, error_message: {error_message}")
        log.logger.error(f'函数{func_signatrue}调用失败, 完全退出')
        return False

    def apply(func, error_message, log_file):
        return Handler.multi_apply(func, range(1, 2), error_message=error_message, log_file=log_file)

