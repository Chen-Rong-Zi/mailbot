from os import remove, path
import sys
import uuid
import subprocess

import json
from   shutil                import rmtree
from   wsgiref.simple_server import make_server

import toml
from   logger   import mailbot_log as log
from   validate import Validator

port = 8080

def del_files(nuuid):
    remove("data/"+nuuid+".dat")
    rmtree("files/"+nuuid)

def receive_json(json_str):
    if not Validator.valid_json(json_str):
        return False
    nuuid = str(uuid.uuid1())
    # nuuid = "af2d31be-973d-11ee-8789-d1a7a5d41e66"
    log.logger.info("收到一次发送邮件请求 uuid: " + nuuid + " user: " + str(json.loads(json_str)['user']))
    writedata = open("data/"+nuuid+".dat", "w", encoding = 'utf-8')
    writedata.write(json_str)
    writedata.close()
    flag = True
    try:
        env = {'config' : json.dumps(config)}
        res1 = subprocess.run(["python", "fetch.py", nuuid], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check = True, env=env)
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
        base.query('select 名称 from Table1')
        sqlc='''UPDATE Table1 set 是否成功发送=True where num=%d'''%(int(id))
        base.query(sqlc)
    del_files()

def update_mail():
    log.logger.info("收到一次更新邮件内容的请求")
    if path.exists('prototype.docx'):
        remove('prototype.docx')
    try:
        base.download_file(ckdic['word'], 'prototype.docx')
    except Exception:
        log.logger.error("下载邮件内容失败！")
        log.logger.exception(Exception)
        return [json.dumps({"status": "ok"}).encode('utf-8')]
    log.logger.info("已完成邮件内容的更新")
    return [json.dumps({"status": "ok"}).encode('utf-8')]

def application(environ, start_response):
    # breakpoint()
    start_response('200 OK', [('Content-Type', 'application/json')])
    request_body  = environ["wsgi.input"].read(int(environ.get("CONTENT_LENGTH", 0)))
    json_str      = request_body.decode('utf-8')
    is_post_valid = Validator.valid_post(json_str)
    if not is_post_valid:
        return [json.dumps({"status": "ok"}).encode('utf-8')]
    ckdic         = is_post_valid

    if 'word' in ckdic:
        update_mail()
    if 'admin' in ckdic:
        log.logger.info("收到一次更新管理员配置的请求")
        if path.exists('admin.toml'):
            remove('admin.toml')
        try:
            base.download_file(ckdic['admin'], 'admin.toml')
        except Exception:
            log.logger.error("下载管理员配置失败！")
            log.logger.exception(Exception)
            return [json.dumps({"status": "ok"}).encode('utf-8')]
        log.logger.info("已完成管理员配置的更新 尝试更新api_token")

        global config
        is_valid  = Validator.valid_config()
        config = is_valid if is_valid else config
        return [json.dumps({"status": "ok"}).encode('utf-8')]
    receive_json(json_str)
    # print(json_str)
    return [json.dumps({"status": "ok"}).encode('utf-8')]


def main():
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

