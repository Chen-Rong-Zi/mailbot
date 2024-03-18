import json
from   wsgiref.simple_server import make_server
import uuid
import subprocess
from   os                    import remove,     path
from   shutil                import rmtree
import logging
from   seatable_api          import Base,       context
import hashlib

server_url  = context.server_url or 'https://table.nju.edu.cn'
api_token   = context.api_token
api_token_2 = context.api_token  or 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJkdGFibGVfdXVpZCI6ImE4N2Q0MTJjLWU4NzMtNDFlYi05NTZkLWNhOTE0Mzg3YWU0NSIsImFwcF9uYW1lIjoiczRsZC5weSIsImV4cCI6MTcwMjgxOTM4NX0.pWPD8rLv4BvqwaSkYD66N88HqO8cHA3TJ65GQ9ai-KA'
key         = 'Xz4uXT7m4KN33vN59D'
port        = 8080

class logger:
    name   = 'mailbot'
    path   = './log/mailbot.log'
    format = '%(asctime)s [%(levelname)s] (%(funcName)s: %(lineno)d): %(message)s'

    def __init__(self):
        '''
            初始化日志

            保存成的文件会在 ./log/fetch.log 下
                通过 path 可以改变保存位置

            默认在控制台输出所有级别的日志，
            在文件中只写入 INFO 及以上级别的日志
        '''

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

        self.logger.setLevel(logging.INFO)

    def __del__(self):
        '''
            析构函数，清空记录器绑定，避免重复输出
        '''

        self.logger.handlers.clear()

log = logger()

def del_files(nuuid):
    remove("data/"+nuuid+".dat")
    rmtree("files/"+nuuid)

def receive_json(json_str):
    nuuid = str(uuid.uuid1())
    # nuuid = "af2d31be-973d-11ee-8789-d1a7a5d41e66"
    log.logger.info("收到一次发送邮件请求 uuid: " + nuuid + " user: " + str(json.loads(json_str)['user']))
    writedata = open("data/"+nuuid+".dat", "w", encoding = 'utf-8')
    writedata.write(json_str)
    writedata.close()
    flag = True
    try:
        res1 = subprocess.run(["python", "fetch.py", nuuid], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check = True)
    except Exception:
        flag = False
        log.logger.error("uuid: " + nuuid + " 获取文件失败")
    if res1.stderr:
        flag = False
        log.logger.error("uuid: " + nuuid + " 获取文件失败")
        print(res1.stderr.decode('utf-8'))
    if flag:
        log.logger.info("uuid: " + nuuid + " 获取文件成功")
        try:
            res2 = subprocess.run(["python", "send_email.py", nuuid], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check = True)
        except Exception:
            flag = False
            log.logger.error("uuid: " + nuuid + " 发送邮件失败")
        if res2.stderr:
            flag = False
            log.logger.error("uuid: " + nuuid + " 发送邮件失败")
            print(res2.stderr.decode('utf-8'))
    if flag:
        log.logger.info("uuid: " + nuuid + " 发送邮件成功")
        id = json.loads(json_str)['id']
        base = Base(api_token, server_url)
        base.auth()
        base.query('select 名称 from Table1')
        sqlc='''UPDATE Table1 set 是否成功发送=True where num=%d'''%(int(id))
        base.query(sqlc)
    del_files()

def application(environ, start_response):
    start_response('200 OK', [('Content-Type', 'application/json')])
    request_body = environ["wsgi.input"].read(int(environ.get("CONTENT_LENGTH", 0)))
    json_str = request_body.decode('utf-8')
    ckdic = json.loads(json_str)
    pwstr = str(ckdic['time']) + key + str(ckdic['user'])
    if hashlib.md5(pwstr.encode(encoding='utf-8')).hexdigest() != ckdic['passwd']:
        log.logger.warn("收到一次非法请求！")
        return [json.dumps({"status": "ok"}).encode('utf-8')]
    if 'word' in ckdic:
        log.logger.info("收到一次更新邮件内容的请求")
        if path.exists('prototype.docx'):
            remove('prototype.docx')
        try:
            base = Base(api_token_2, server_url)
            base.auth()
            base.download_file(ckdic['word'], 'prototype.docx')
        except Exception:
            log.logger.error("下载邮件内容失败！")
            log.logger.exception(Exception)
            return [json.dumps({"status": "ok"}).encode('utf-8')]
        log.logger.info("已完成邮件内容的更新")
        return [json.dumps({"status": "ok"}).encode('utf-8')]
    if 'admin' in ckdic:
        log.logger.info("收到一次更新管理员配置的请求")
        if path.exists('admin.config'):
            remove('admin.config')
        try:
            base = Base(api_token_2, server_url)
            base.auth()
            base.download_file(ckdic['admin'], 'admin.config')
        except Exception:
            log.logger.error("下载管理员配置失败！")
            log.logger.exception(Exception)
            return [json.dumps({"status": "ok"}).encode('utf-8')]
        log.logger.info("已完成管理员配置的更新 尝试更新api_token")
        with open("admin.config", 'r', encoding='utf-8') as file:
            for line in file.readlines():
                if 'api_token' in line:
                    line = line.split('=', 1)
                    global api_token
                    api_token = line[1].strip()
        return [json.dumps({"status": "ok"}).encode('utf-8')]
    receive_json(json_str)
    # print(json_str)
    return [json.dumps({"status": "ok"}).encode('utf-8')]

if __name__ == "__main__":
    with open("admin.config", 'r', encoding='utf-8') as file:
        for line in file.readlines():
            if 'api_token' in line:
                line = line.split('=', 1)
                api_token = line[1].strip()
    httpd = make_server("0.0.0.0", port, application)
    log.logger.info("Mailbot开始运行并监听端口{0}".format(port))
    httpd.serve_forever()

