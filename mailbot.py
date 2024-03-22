from os import remove, path
import sys
import subprocess

import json
import shutil
from   wsgiref.simple_server import make_server

import toml
from   logger   import mailbot_log as log
from   validate import Validator
from   handler  import Handler


def set_config():
    global config
    is_valid = Validator.valid_config()
    if is_valid:
        config = is_valid
        log.logger.info('用户配置修改成功')
    else:
        log.logger.info('用户配置不合法，修改失败')

def send_email_request(post):
    log.logger.info("收到一次发送邮件请求 user: " + str(post['user']))
        f.write(json.dumps(post, ensure_ascii = False))
    flag = True

    try:
        user = post['user']
        env = {'config' : json.dumps(config), 'data' : json.dumps(config)}
        res1 = subprocess.run(["python", "fetch.py", user], stdout = subprocess.PIPE, stderr = subprocess.PIPE, check = True, env = env)
    except Exception:
        flag = False
        log.logger.error("user: " + user + " 获取文件失败")
    if res1.stderr:
        flag = False
        log.logger.error("user: " + user + " 获取文件失败")
        print(res1.stderr.decode('utf-8'))
    if flag:
        log.logger.info("user: " + user + " 获取文件成功")
        try:
            res2 = subprocess.run(["python", "send_email.py", user], stdout = subprocess.PIPE, stderr = subprocess.PIPE, check = True)
        except Exception:
            flag = False
            log.logger.error("user: " + user + " 发送邮件失败")
        if res2.stderr:
            flag = False
            log.logger.error("user: " + user + " 发送邮件失败")
            print(res2.stderr.decode('utf-8'))
    if flag:
        log.logger.info("user: " + user + " 发送邮件成功")
        id = json.loads(json_str)['id']
        base.query('select 名称 from Table1')
        sqlc = '''UPDATE Table1 set 是否成功发送 = True where num = %d''' % (int(id))
        base.query(sqlc)

def update_mail():
    log.logger.info("收到一次更新邮件内容的请求")
    download_func = lambda : base.download_file(ckdic['word'], './tmp/prototype.docx')
    result        = Handler.multi_apply(download_func, range(3))

    if result:
        shutil.move('./tmp/prototype.docx', './prototype.docx')
        log.logger.info("已完成邮件内容的更新")
    return [json.dumps({"status": "ok"}).encode('utf-8')]

def update_config():
    log.logger.info("收到一次更新管理员配置的请求")
    download_func = lambda : base.download_file(post['admin'], './tmp/admin.toml')
    result        = Handler.multi_apply(download_func, range(3))

    if result:
        shutil.move('./tmp/admin.toml', './admin.toml')
        set_config()
        log.logger.info("已完成更新管理员配置文件")
    return [json.dumps({"status": "ok"}).encode('utf-8')]

def application(environ, start_response):
    start_response('200 OK', [('Content-Type', 'application/json')])
    request_body  = environ["wsgi.input"].read(int(environ.get("CONTENT_LENGTH", 0)))
    json_str      = request_body.decode('utf-8')
    is_post_valid = Validator.valid_post(json_str)
    if not is_post_valid:
        return [json.dumps({"status": "ok"}).encode('utf-8')]

    post = is_post_valid
    if 'word'  in post:
        return update_mail()
    if 'admin' in post:
        return update_config()
    else:
        send_email_request(post)
    return [json.dumps({"status": "ok"}).encode('utf-8')]


def main():
    port  = config['mailbot']['port']
    httpd = make_server("0.0.0.0", port, application)
    log.logger.info("Mailbot开始运行并监听端口{0}".format(port))
    httpd.serve_forever()

if __name__ == "__main__":
    requirements = [Validator.valid_config(), Validator.valid_base()]
    valid        = all(requirements)
    if not valid:
        sys.exit(1)
    config       = requirements[0]
    base         = requirements[1]
    main()

