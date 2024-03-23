from util.logger import mailbot_log
from util.logger import fetch_log

def forever():
    n = 0
    while 1:
        n += 1
        yield n

class Handler:
    def multi_apply(func, times=forever(), error_message='', sucess_message='', log_file='fetch.log'):
        log = {'fetch.log' : fetch_log, 'mailbot.log' : mailbot_log}[log_file]
        for i in times:
            try:
                result = func()
                log.logger.info(f"调用成功，总计尝试{i}次")
                log.logger.info(sucess_message)
                # 避免func返回None
                return result if result else 'sucess'
            except Exception as err:
                func_signatrue = str(func).split()[1]
                log.logger.error(f"函数{func_signatrue}第{i}次调用失败！")
                log.logger.error(err)
                log.logger.error(error_message)
        log.logger.error(f'函数{func_signatrue}调用失败, 完全退出')
        return False

    def apply(func, error_message, log_file):
        return Handler.multi_apply(func, range(1, 2), error_message=error_message, log_file=log_file)

