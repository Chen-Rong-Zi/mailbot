import sys
from   os       import environ
import subprocess

import json
import shutil
import toml
from   wsgiref.simple_server import make_server

from   util.logger   import mailbot_log as log
from   util.validate import Validator
from   util.handler  import Handler


def set_config():
    global config
    is_valid = Validator.valid_config()
    if is_valid:
        config = is_valid
        log.logger.info('用户配置修改成功')
    else:
        log.logger.info('用户配置不合法，修改失败')

def email_request(post):
    log.logger.error(f"收到一次发送邮件请求 user: {str(post['user'])}")

    user = post['user']
    environ.update({'config' : json.dumps(config), 'data' : json.dumps(post)})
    proc_func_maker = lambda command : lambda : subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, env=environ)

    crawer          = proc_func_maker(["python3", "fetch.py",     str(user)])
    is_crawer_fine  = Handler.apply(crawer, '获取资料失败', 'mailbot.log')
    if not is_crawer_fine:
        return [json.dumps({"status": "ok"}).encode('utf-8')]

    mail_program = proc_func_maker(["python3", "send_mail.py", str(user)])
    is_mail_fine = Handler.apply(mail_program, '发送邮件失败', 'mailbot.log')
    if not is_mail_fine:
        return [json.dumps({"status": "ok"}).encode('utf-8')]

    base.query('select 名称 from Table1')
    sqlc = f'''UPDATE Table1 set 是否成功发送 = True where num = {int(post['id'])}'''
    base.query(sqlc)
    log.logger.info(f"user: {user} 发送邮件成功")
    return [json.dumps({"status": "ok"}).encode('utf-8')]

def update_mail():
    log.logger.info("收到一次更新邮件内容的请求")
    download_func = lambda : base.download_file(ckdic['word'], './tmp/prototype.docx')
    result        = Handler.multi_apply(download_func, range(3), log_file='mailbot.log')

    if result:
        shutil.move('./tmp/prototype.docx', './prototype.docx')
        log.logger.info("已完成邮件内容的更新")
    return [json.dumps({"status": "ok"}).encode('utf-8')]

def update_config():
    log.logger.info("收到一次更新管理员配置的请求")
    download_func = lambda : base.download_file(post['admin'], './tmp/admin.toml')
    result        = Handler.multi_apply(download_func, range(3), log_file='mailbot.log')
    if not result:
        return [json.dumps({"status": "ok"}).encode('utf-8')]

    shutil.move('./tmp/admin.toml', './admin.toml')
    set_config()
    log.logger.info("已完成更新管理员配置文件")
    return [json.dumps({"status": "ok", 'result' : '用户配置不合法'}).encode('utf-8')]


def application(environ, start_response):
    start_response('200 OK', [('Content-Type', 'application/json')])
    request_body  = environ["wsgi.input"].read(int(environ.get("CONTENT_LENGTH", 0)))
    json_str      = request_body.decode('utf-8')
    is_post_valid = Validator.valid_post(json_str)
    if not is_post_valid:
        return [json.dumps({"status": "ok", 'result' : 'json不合法'}).encode('utf-8')]

    post = is_post_valid
    if 'word'  in post:
        return update_mail()
    if 'admin' in post:
        return update_config()
    else:
        email_request(post)
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

