import sys
import logging
import datetime

class StdoutRedirector(logging.Handler):
    def __init__(self, level=logging.NOTSET, content=''):
        super().__init__(level=level)  # 设置处理器的日志级别
        self.content = content
        self.prefix = lambda : datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.prefix = lambda : ''

    def emit(self, record):
        self.content += f"{self.prefix()}    {record.msg}"

    def format(self, record):
        return record.msg
    
    def error(self):
        self.write(self, text)


