import sys
import os
from   os                    import environ
import subprocess

import json
import datetime
import shutil
import toml
from   wsgiref.simple_server import make_server

from   util.logger           import mailbot_log as log, send_email_log
from   util.validate         import Validator
from   util.handler          import Handler
from   util.stream           import StdoutRedirector


def set_config(configuration):
    global config
    config = configuration

def set_column(column, result, post):
    base.query(f"""UPDATE Table1 set {column} = {result} where 学号 = {int(post["stu_id"])} and 申请时间 = '{post["application_time"]}'""")

def email_request(post):
    log.logger.error(f"收到一次发送邮件请求 user: {str(post['stu_id'])}")
    base.query('select 名称 from Table1')

    stu_id = post['stu_id']
    # config: 配置信息，data: 用户信息
    environ.update({'config' : json.dumps(config), 'data' : json.dumps(post)})
    proc_func_maker = lambda command : lambda : subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, env=environ)

    crawer          = proc_func_maker(["python3", "fetch.py",  str(stu_id)])
    is_crawer_fine  = Handler.apply(crawer, '获取资料失败', 'mailbot.log')
    if not is_crawer_fine:
        set_column('材料是否下载', "False", post)
        return [json.dumps({"status": "ok", "result" : "材料下载失败"}).encode('utf-8')]

    mail_program = proc_func_maker(["python3", "send_email.py", str(stu_id), 'save'])
    is_mail_fine = Handler.apply(mail_program, '邮件保存失败', 'mailbot.log')
    if not is_mail_fine:
        # set_column('邮件是否生成', post)
        set_column('邮件是否生成', 'False', post)
        return [json.dumps({"status": "ok", "result" : '邮件保存失败'}).encode('utf-8')]

    set_column('邮件是否生成', 'True', post)
    set_column('材料是否下载', 'True', post)
    return [json.dumps({"status": "ok", 'result' : '邮件保存成功'}).encode('utf-8')]

def send_email_request(post):
    redir = StdoutRedirector()
    log.logger.addHandler(redir)
    stu_id = post['stu_id']
    filepath = f"./emails/{stu_id}.eml"
    if not os.path.exists(filepath):
        return [json.dumps({"status": "ok", 'result' : f"学号为{stu_id}没有发送邮件请求"}).encode('utf-8')]

    environ.update({'config' : json.dumps(config), 'data' : json.dumps(post)})
    proc_func_maker = lambda command : lambda : subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, env=environ)
    mail_program    = proc_func_maker(["python3", "send_email.py", str(stu_id), 'send'])
    is_mail_fine    = Handler.apply(mail_program, '邮件发送失败', 'mailbot.log')
    if not is_mail_fine:
        set_column("邮件是否发送", "False", post)
        log.logger.removeHandler(redir)
        return [json.dumps({"status": "ok", "result" : '邮件发送失败', "error_msg" : redir.content}).encode('utf-8')]
    set_column("邮件是否发送", "True", post)
    set_column("邮件发送时间", f"'{datetime.datetime.now()}'", post)
    return [json.dumps({"status": "ok", "result" : '邮件发送成功'}).encode('utf-8')]


def get_preview(post):
    filepath = f"./emails/{post['stu_id']}.eml"
    if not os.path.exists(filepath):
        log.logger.error(f'不存在{filepath} 的邮件')
        return [json.dumps({"status": "ok", 'result' : f"学号为{post['stu_id']}没有发送邮件请求"}).encode('utf-8')]
    with open(filepath) as f:
        content = f.read()
    log.logger.error(f'发送学号为{post["stu_id"]}的邮件')
    return [json.dumps({"status": "ok", 'result' : 'ok',  'email' : content, "stu_id" : post['stu_id']}).encode('utf-8')]

def update_mail():
    log.logger.info("收到一次更新邮件内容的请求")
    download_func = lambda : base.download_file(ckdic['word'], './tmp/prototype.docx')
    result        = Handler.multi_apply(download_func, range(3), log_file='mailbot.log')

    if result:
        shutil.move('./tmp/prototype.docx', './prototype.docx')
        log.logger.info("已完成邮件内容的更新")
    return [json.dumps({"status": "ok"}).encode('utf-8')]

def update_config(configuration):
    redir = StdoutRedirector()
    log.logger.addHandler(redir)
    log.logger.info("收到一次更新管理员配置的请求")
    is_config_valid = Validator.valid_config(configuration)
    if not is_config_valid:
        log.logger.removeHandler(redir)
        return [json.dumps({"status": "ok", 'result' : '配置文件更新失败，用户配置不合法', 'error_msg' : redir.content}).encode('utf-8')]

    new_config, base = is_config_valid
    set_config(new_config)
    log.logger.info("已完成更新管理员配置文件")
    log.logger.removeHandler(redir)
    return [json.dumps({"status": "ok", "result" : "更新配置成功", 'error_msg' : redir.content}).encode('utf-8')]


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
    if 'configuration' in post:
        return update_config(post['configuration'])
    if 'send' in post:
        return send_email_request(post)
    if 'preview' in post:
        return get_preview(post)
    if post['stu_id'] == 'client':
        return [json.dumps({"status": "ok", "result" : "客户端已连接"}).encode('utf-8')]
    if 'generate' in post:
        return email_request(post)
    else:
        return email_request(post)

    return [json.dumps({"status": "ok"}).encode('utf-8')]

def main():
    port  = config['mailbot']['port']
    httpd = make_server("0.0.0.0", port, application)
    log.logger.info("Mailbot开始运行并监听端口{0}".format(port))
    httpd.serve_forever()

if __name__ == "__main__":
    requirements = [Validator.valid_config()]
    valid        = all(requirements)
    if not valid:
        sys.exit(1)
    config, base = requirements[0]
    main()

