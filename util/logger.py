import sys
import logging

class logger:
    format = '%(asctime)s [%(levelname)s] (%(funcName)s: %(lineno)d): %(message)s'

    def __init__(self, name, path):
        '''
            初始化日志

            保存成的文件会在 ./log/fetch.log 下
                通过 path 可以改变保存位置

            默认在控制台输出所有级别的日志，
            在文件中只写入 INFO 及以上级别的日志
        '''
        self.name   = name
        self.path   = path
        self.logger = logging.getLogger(self.name)
        # 默认不向父记录器传递日志信息
        self.logger.propagate = False
        self.format = logging.Formatter(self.format)

        self.console = logging.StreamHandler()
        self.console.setLevel(logging.INFO)
        self.console.setFormatter(self.format)
        self.logger.addHandler(self.console)

        self.file = logging.FileHandler(
              filename=self.path, mode='a', encoding='utf-8')
        self.file.setLevel(logging.INFO)
        self.file.setFormatter(self.format)
        self.logger.addHandler(self.file)

        stream_handler = logging.StreamHandler(sys.stdout)
        self.logger.addHandler(stream_handler)
        self.logger.setLevel(logging.INFO)

    def __del__(self):
        '''
            析构函数，清空记录器绑定，避免重复输出
        '''

        self.logger.handlers.clear()


fetch_log      = logger('fetch',     './log/fetch.log')
mailbot_log    = logger('mailbot',   './log/mailbot.log')
send_email_log = logger('send_mail', './log/send_mail.log')
